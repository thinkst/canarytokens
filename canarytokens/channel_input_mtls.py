import json
import random
from datetime import datetime
from ipaddress import IPv4Address
from typing import TypedDict

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
from canarytokens.exceptions import NoCanarytokenFound, NoCanarydropFound
from canarytokens.models import KubeCerts, KubeconfigTokenHit
from canarytokens.queries import (  # get_kc_hits,; save_kc_hit_for_aggregation,
    get_canarydrop,
    get_certificate,
    is_tor_relay,
    save_certificate,
    save_kc_endpoint,
)
from canarytokens.settings import FrontendSettings, SwitchboardSettings
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
    def __init__(self, factory, headers, bodies, enricher=None):
        self.factory = factory
        self.headers = headers
        self.bodies = bodies
        self.lines = []
        self.enricher = enricher
        self.last_hit = datetime.utcnow()

    def lineReceived(self, line: bytes):
        self.lines.append(line)
        if not line:
            self.send_response()

    def send_response(self):
        client = self.transport.getPeer()

        req_uri = self.lines[0].split(b" ")[1]

        headers = {
            line.split(b":")[0]: line.split(b":")[1].strip()
            for line in self.lines[2:-1]
        }
        user_agent = headers.get(b"User-Agent", "Unknown")

        try:
            peer_certificate = Certificate.peerFromTransport(self.transport)
            f = peer_certificate.digest()
            self.sendLine(b"HTTP/1.1 401 Unauthorized")
            self.sendLine(self.headers())
            self.sendLine(b"")
            self.transport.write(json.dumps(self.bodies["unauthorized"]).encode())
            self.transport.loseConnection()
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
            log.error(f"CertificateError Exception: {e}")
            self.sendLine(b"HTTP/1.1 403 Forbidden")
            self.sendLine(self.headers())
            self.sendLine(b"")
            response = self.bodies["forbidden"]
            response["message"] = response["message"].format(req_uri.split("?")[0])
            self.transport.write(json.dumps(response).encode())
            self.transport.loseConnection()
        except Exception as e:
            log.error(f"Exception send_response: {e}")
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
        except (NoCanarydropFound, NoCanarytokenFound):
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
        ca_redis_key, username, ip=None, is_server_cert=False
    ) -> KubeCerts:
        log.debug("generating new certificate")
        ca = get_certificate(ca_redis_key)
        if not ca:
            log.warn("CA with key {} not found in redis".format(ca_redis_key))
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

        ca_extension = X509Extension(b"basicConstraints", True, b"CA:FALSE")
        key_usage = X509Extension(
            b"keyUsage", True, b"digitalSignature,keyEncipherment"
        )

        if ip:
            san_list = [
                "IP:{}".format(ip),
                "DNS:kubernetes",
                "DNS:kubernetes.default",
                "DNS:kubernetes.default.svc",
                "DNS:kubernetes.default.svc.cluster",
                "DNS:kubernetes.svc.cluster.local",
            ]
        else:
            san_list = None

        extensions = [
            ca_extension,
            X509Extension(
                b"authorityKeyIdentifier", False, b"keyid", issuer=cert_authority
            ),
            (
                X509Extension(b"extendedKeyUsage", True, b"serverAuth")
                if is_server_cert
                else X509Extension(b"extendedKeyUsage", True, b"clientAuth")
            ),
            key_usage,
        ]
        if san_list:
            extensions.append(
                X509Extension(b"subjectAltName", False, ", ".join(san_list).encode())
            )

        x509.add_extensions(extensions)

        x509.set_issuer(cert_authority.get_subject())
        x509.set_pubkey(client_key)
        x509.gmtime_adj_notBefore(0)
        # default certificate validity is 1 year
        x509.gmtime_adj_notAfter(1 * 365 * 24 * 60 * 60 - 1)
        x509.sign(ca_key, "sha256")

        return {
            "f": mTLS._get_digest(dump_certificate(FILETYPE_PEM, x509)),
            "c": dump_certificate(FILETYPE_PEM, x509),
            "k": dump_privatekey(FILETYPE_PEM, client_key),
        }

    @staticmethod
    def generate_new_ca(username) -> KubeCerts:
        log.debug("generating new certificate")
        client_key = PKey()
        client_key.generate_key(TYPE_RSA, 4096)

        x509 = X509()
        x509.set_version(2)
        x509.set_serial_number(random.randint(0, 100000000))

        client_subj = x509.get_subject()
        client_subj.commonName = username

        ca_extension = X509Extension(b"basicConstraints", True, b"CA:TRUE, pathlen:0")
        key_usage = X509Extension(
            b"keyUsage", False, b"digitalSignature,keyCertSign,keyEncipherment"
        )

        x509.add_extensions(
            [
                ca_extension,
                X509Extension(b"subjectKeyIdentifier", False, b"hash", subject=x509),
                key_usage,
            ]
        )

        x509.set_issuer(client_subj)
        x509.set_pubkey(client_key)
        x509.gmtime_adj_notBefore(0)
        # default ca validity is 10 years with kubeadm
        x509.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60 - 1)
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
        switchboard_hostname: str,
        switchboard_scheme: str,
        switchboard: Switchboard,
        channel_name=None,
        enricher=None,
    ):
        self.headers = headers
        self.bodies = bodies
        self.enricher = enricher

        self.switchboard = switchboard
        InputChannel.__init__(
            self,
            switchboard=self.switchboard,
            switchboard_hostname=switchboard_hostname,
            switchboard_scheme=switchboard_scheme,
            name=channel_name if channel_name is not None else self.CHANNEL,
            unique_channel=False,
        )

    def buildProtocol(self, addr: str) -> mTLS:
        return mTLS(
            factory=self,
            headers=self.headers,
            bodies=self.bodies,
            enricher=self.enricher,
        )


class ChannelKubeConfig:
    def __init__(
        self,
        frontend_settings: FrontendSettings,
        switchboard_settings: SwitchboardSettings,
        switchboard=None,
    ):
        from canarytokens import kubeconfig

        self.client_ca_redis_key = kubeconfig.ClientCA
        self.server_ca_redis_key = kubeconfig.ServerCA
        self.server_cert_redis_key = kubeconfig.ServerCert
        self.port = switchboard_settings.CHANNEL_MTLS_KUBECONFIG_PORT
        self.ip = IPv4Address(frontend_settings.PUBLIC_IP)
        self.channel_name = INPUT_CHANNEL_MTLS

        save_kc_endpoint(ip=self.ip, port=self.port)

        kc = kubeconfig.KubeConfig(
            client_ca_redis_key=self.client_ca_redis_key,
            server_ca_redis_key=self.server_ca_redis_key,
            server_endpoint_ip=self.ip,
            server_endpoint_port=self.port,
        )
        factory = mTLSFactory(
            headers=kc.kc_headers,
            bodies=kc.bodies,
            channel_name=self.channel_name,
            enricher=None,
            switchboard_scheme=switchboard_settings.SWITCHBOARD_SCHEME,
            switchboard_hostname=frontend_settings.DOMAINS[0],
            switchboard=switchboard,
        )

        self.service = SSLServer(
            self.port,
            factory,
            self._get_ssl_context(
                client_ca_redis_key=self.client_ca_redis_key,
                server_ca_redis_key=self.server_ca_redis_key,
                server_cert_redis_key=self.server_cert_redis_key,
                ip=self.ip,
            ),
        )

    @staticmethod
    def _get_ssl_context(
        *,
        client_ca_redis_key: str,
        server_ca_redis_key: str,
        server_cert_redis_key: str,
        ip: str,
    ) -> CertificateOptions:
        log.debug("_get_ssl_context")

        certs = {}
        # fmt: off
        params = [
            (client_ca_redis_key, None, "kubernetes-ca", Certificate),
            (server_ca_redis_key, None, "kubernetes-ca", Certificate),
            (server_cert_redis_key, server_ca_redis_key, "kube-apiserver", PrivateCertificate),
        ]
        # fmt: on
        for redis_key, issuer, username, kind in params:
            log.debug(f"checking for: {redis_key}")
            try:
                # if it's there we use it
                cert = get_certificate(redis_key)
                log.debug("cert found")
            except LookupError:
                # Generate cert if not found.
                log.debug("generating cert")
                if redis_key.endswith("_ca"):
                    cert = mTLS.generate_new_ca(username=username)
                else:
                    cert = mTLS.generate_new_certificate(
                        ca_redis_key=issuer,
                        username=username,
                        ip=ip,
                        is_server_cert=True,
                    )

            save_certificate(redis_key, cert)

            cert_pem = "{}\n{}".format(
                cert.get("c").decode(),
                cert.get("k").decode(),
            )
            certs[redis_key] = kind.loadPEM(cert_pem)

        return certs[server_cert_redis_key].options(certs[client_ca_redis_key])
