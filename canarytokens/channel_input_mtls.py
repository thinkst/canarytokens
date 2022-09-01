import json
import random
from datetime import datetime
from ipaddress import IPv4Address
from typing import Optional, TypedDict

from OpenSSL.crypto import (
    FILETYPE_PEM,
    TYPE_RSA,
    X509,
    PKey,
    X509Extension,
    dump_certificate,
    dump_privatekey,
    load_certificate,
    load_privatekey,
)
from twisted.application.internet import SSLServer
from twisted.internet import defer
from twisted.internet.error import CertificateError
from twisted.internet.protocol import Factory
from twisted.internet.ssl import Certificate, CertificateOptions, PrivateCertificate
from twisted.logger import Logger
from twisted.protocols import basic

from canarytokens import queries
from canarytokens.channel import InputChannel
from canarytokens.constants import INPUT_CHANNEL_MTLS
from canarytokens.exceptions import NoCanarytokenFound, NoCanarytokenPresent
from canarytokens.models import KubeCerts, KubeconfigTokenHit
from canarytokens.queries import (  # get_kc_hits,; save_kc_hit_for_aggregation,
    get_canarydrop,
    get_certificate,
    is_tor_relay,
    save_certificate,
    save_kc_endpoint,
)
from canarytokens.settings import BackendSettings, Settings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

log = Logger()


class ChirpData(TypedDict):
    # TODO: rename these to something meaningful.
    # DESIGN: Should this simple be a KubeconfigTokenHit?
    #         Leaving same as v2 for now.
    f: bytes
    tf: bytes
    ip: str
    useragent: str
    location: str


class mTLS(basic.LineReceiver):
    def __init__(self, factory, headers, bodies, ca_cert_path, enricher=None):
        self.factory = factory
        self.headers = headers
        self.bodies = bodies
        self.client_ca_cert_path = ca_cert_path
        self.lines = []
        self.enricher = enricher
        self.last_hit = datetime.utcnow()

    def lineReceived(self, line: bytes):
        log.debug(f"lineReceived: {line!r}")
        self.lines.append(line)
        if not line:
            self.send_response()

    def send_response(self):
        log.debug("send_response")
        client = self.transport.getPeer()

        req_uri = self.lines[0].split(b" ")[1]

        headers = {
            line.split(b":")[0]: line.split(b":")[1].strip()
            for line in self.lines[2:-1]
        }
        user_agent = headers.get("User-Agent", "Unknown")

        try:
            log.debug("trying to get cert")
            peer_certificate = Certificate.peerFromTransport(self.transport)
            f = peer_certificate.digest()
            self.sendLine(b"HTTP/1.1 401 Unauthorized")
            self.sendLine(self.headers())
            self.sendLine(b"")
            self.transport.write(json.dumps(self.bodies["unauthorized"]).encode())
            self.transport.loseConnection()
            log.debug("all good, chirping.")
            self.chirp(
                {
                    "f": f,
                    "tf": f.replace(b":", b"")[:25].lower(),
                    "ip": client.host,
                    "useragent": user_agent,
                    "location": req_uri.split(b"?")[0],
                }
            )

        except CertificateError as e:
            log.error("CertificateError Exception: {}".format(e))
            self.sendLine(b"HTTP/1.1 403 Forbidden")
            self.sendLine(self.headers())
            self.sendLine(b"")
            response = self.bodies["forbidden"]
            response["message"] = response["message"].format(req_uri.split("?")[0])
            self.transport.write(json.dumps(response).encode())
            self.transport.loseConnection()
        except Exception as e:
            log.error("Exception send_response: {}".format(e))
            self.sendLine(b"HTTP/1.1 400 Bad Request")
            self.sendLine(self.headers())
            self.sendLine(b"")
            self.transport.write(json.dumps(self.bodies["bad"]).encode())
            self.transport.loseConnection()

        d = defer.Deferred()
        d.callback("Success")
        return d

    def chirp(self, trigger: ChirpData):
        """Builds the hit and dispatches the alert."""
        token = Canarytoken(value=trigger["tf"].decode())
        try:
            canarydrop = get_canarydrop(canarytoken=token)
        except (NoCanarytokenPresent, NoCanarytokenFound):
            log.warn(
                "No token for {tf} | Cert: {f}".format(tf=trigger["tf"], f=trigger["f"])
            )
            raise
        token_hit = KubeconfigTokenHit(
            time_of_hit=datetime.utcnow().strftime("%s.%f"),
            src_ip=trigger["ip"],
            useragent=trigger["useragent"],
            location=trigger["location"],
            # TODO: 3rd party call here - remove this.
            geo_info=queries.get_geoinfo(ip=trigger["ip"]),
            input_channel=INPUT_CHANNEL_MTLS,
            is_tor_relay=is_tor_relay(ip=trigger["ip"]),
        )
        canarydrop.add_canarydrop_hit(token_hit=token_hit)
        if self.enricher:
            self.enricher(trigger, canarydrop, self.factory.dispatch)
        else:
            self.factory.dispatch(
                canarydrop=canarydrop,
                token_hit=token_hit,
            )

    @staticmethod
    def generate_new_certificate(
        ca_cert_path, username, is_ca_generation_request=False, ip=None
    ) -> KubeCerts:
        log.debug("generating new certificate")
        if not is_ca_generation_request:
            ca = get_certificate(ca_cert_path)
            if not ca:
                log.warn("CA with key {} not found in redis".format(ca_cert_path))
                return None

            ca_key = load_privatekey(FILETYPE_PEM, ca.get("k"))
            cert_authority = load_certificate(FILETYPE_PEM, ca.get("c"))

            client_key = PKey()
            client_key.generate_key(TYPE_RSA, 4096)

            x509 = X509()
            x509.set_version(2)
            x509.set_serial_number(random.randint(0, 100000000))

            client_subj = x509.get_subject()
            client_subj.commonName = username

            ca_extension = X509Extension(b"basicConstraints", False, b"CA:FALSE")
            key_usage = X509Extension(b"keyUsage", True, b"digitalSignature")

            if username == "kubernetes-apiserver":
                san_list = [
                    "IP:{}".format(ip),
                    "DNS:kubernetes",
                    "DNS:kubernetes.default",
                    "DNS:kubernetes.default.svc",
                    "DNS:kubernetes.default.svc.cluster",
                    "DNS:kubernetes.svc.cluster.local",
                ]
                x509.add_extensions(
                    [
                        ca_extension,
                        X509Extension(
                            b"subjectKeyIdentifier", False, b"hash", subject=x509
                        ),
                        X509Extension(b"extendedKeyUsage", True, b"clientAuth"),
                        X509Extension(
                            b"subjectAltName", False, ", ".join(san_list).encode()
                        ),
                        key_usage,
                    ]
                )
            else:
                x509.add_extensions(
                    [
                        ca_extension,
                        X509Extension(
                            b"subjectKeyIdentifier", False, b"hash", subject=x509
                        ),
                        X509Extension(b"extendedKeyUsage", True, b"clientAuth"),
                        key_usage,
                    ]
                )

            x509.set_issuer(cert_authority.get_subject())
            x509.set_pubkey(client_key)
            x509.gmtime_adj_notBefore(0)
            # default certificate validity is 1 year
            x509.gmtime_adj_notAfter(1 * 365 * 24 * 60 * 60 - 1)
            x509.sign(ca_key, "sha256")
        else:
            client_key = PKey()
            client_key.generate_key(TYPE_RSA, 4096)

            x509 = X509()
            x509.set_version(2)
            x509.set_serial_number(random.randint(0, 100000000))

            client_subj = x509.get_subject()
            client_subj.commonName = username

            ca_extension = X509Extension(
                b"basicConstraints", True, b"CA:TRUE, pathlen:0"
            )
            key_usage = X509Extension(
                b"keyUsage", False, b"cRLSign,digitalSignature,keyCertSign"
            )

            x509.add_extensions(
                [
                    ca_extension,
                    X509Extension(
                        b"subjectKeyIdentifier", False, b"hash", subject=x509
                    ),
                    X509Extension(b"extendedKeyUsage", True, b"clientAuth"),
                    key_usage,
                ]
            )

            x509.set_issuer(client_subj)
            x509.set_pubkey(client_key)
            x509.gmtime_adj_notBefore(0)
            # default certificate validity is 1 year
            x509.gmtime_adj_notAfter(1 * 365 * 24 * 60 * 60 - 1)
            x509.sign(client_key, "sha256")

        return {
            "f": mTLS._get_digest(dump_certificate(FILETYPE_PEM, x509)),
            "c": dump_certificate(FILETYPE_PEM, x509),
            "k": dump_privatekey(FILETYPE_PEM, client_key),
        }

    @staticmethod
    def _get_digest(cert) -> bytes:
        from twisted.internet.ssl import Certificate

        return Certificate.loadPEM(cert).digest()


class mTLSFactory(Factory, InputChannel):
    CHANNEL = INPUT_CHANNEL_MTLS
    protocol = mTLS

    def __init__(
        self,
        headers,
        bodies,
        ca_cert_path,
        backend_hostname: str,
        backend_scheme: str,
        switchboard: Switchboard,
        channel_name=None,
        enricher=None,
    ):
        self.headers = headers
        self.bodies = bodies
        self.client_ca_cert_path = ca_cert_path
        self.enricher = enricher

        self.switchboard = switchboard
        InputChannel.__init__(
            self,
            switchboard=self.switchboard,
            backend_hostname=backend_hostname,
            backend_scheme=backend_scheme,
            name=channel_name if channel_name is not None else self.CHANNEL,
            unique_channel=False,
        )

    def buildProtocol(self, addr: str) -> mTLS:
        return mTLS(
            factory=self,
            headers=self.headers,
            bodies=self.bodies,
            ca_cert_path=self.client_ca_cert_path,
            enricher=self.enricher,
        )


class ChannelKubeConfig:
    def __init__(
        self,
        backend_settings: BackendSettings,
        switchboard_settings: Settings,
        switchboard=None,
    ):
        from canarytokens import kubeconfig

        self.client_ca_cert_path = kubeconfig.ClientCA
        self.server_cert_path = kubeconfig.ServerCA
        self.port = switchboard_settings.CHANNEL_MTLS_KUBECONFIG_PORT
        self.ip = IPv4Address(switchboard_settings.PUBLIC_IP)
        self.channel_name = INPUT_CHANNEL_MTLS

        save_kc_endpoint(ip=self.ip, port=self.port)

        kc = kubeconfig.KubeConfig(
            ca_cert_path=self.client_ca_cert_path,
            server_endpoint_ip=self.ip,
            server_endpoint_port=self.port,
        )
        factory = mTLSFactory(
            headers=kc.kc_headers,
            bodies=kc.bodies,
            ca_cert_path=self.client_ca_cert_path,
            channel_name=self.channel_name,
            enricher=None,
            backend_scheme=backend_settings.BACKEND_SCHEME,
            backend_hostname=backend_settings.BACKEND_HOSTNAME,
            switchboard=switchboard,
        )

        self.service = SSLServer(
            self.port,
            factory,
            self._get_ssl_context(
                client_ca_cert_path=self.client_ca_cert_path,
                server_cert_path=self.server_cert_path,
                ip=self.ip,
            ),
        )

    @staticmethod
    def get_or_create_ca(
        ca_cert_path: str,
        username: str,
        ip: Optional[str] = None,
        private: bool = False,
    ):
        """"""
        log.debug("get_or_create ca")
        try:
            ca = get_certificate(ca_cert_path)
            log.debug("cert found")
        except LookupError:
            # Generate cert if not found.
            log.debug("generating cert")
            ca = mTLS.generate_new_certificate(
                is_ca_generation_request=True,
                ca_cert_path=ca_cert_path,
                username=username,
                ip=ip,
            )
            save_certificate(ca_cert_path, ca)
        log.debug(f"{ca = }")

        ca_pem = "{}\n{}".format(
            ca.get("c").decode(),
            ca.get("k").decode(),
        )
        if private:
            log.debug("private")
            return PrivateCertificate.loadPEM(ca_pem)
        else:
            log.debug("not private")
            return Certificate.loadPEM(ca_pem)

    @staticmethod
    def _get_ssl_context(
        *, client_ca_cert_path: str, server_cert_path: str, ip: str
    ) -> CertificateOptions:
        # TODO: refactor this function and improve code complexity.
        log.debug("_get_ssl_context")
        client_cert = ChannelKubeConfig.get_or_create_ca(
            ca_cert_path=client_ca_cert_path,
            username="kubernetes-ca",
        )
        server_cert = ChannelKubeConfig.get_or_create_ca(
            ca_cert_path=server_cert_path,
            username="kubernetes-apiserver",
        )

        server_ca_cert_path = server_cert_path + "_ca"
        server_cert = ChannelKubeConfig.get_or_create_ca(
            ca_cert_path=server_ca_cert_path,
            username="kubernetes-apiserver",
            ip=ip,
            private=True,
        )

        return server_cert.options(client_cert)
