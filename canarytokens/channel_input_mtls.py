import json
import random
from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address
from typing import TypedDict

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

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
        ca = get_certificate(ca_redis_key)
        if not ca:
            log.warn("CA with key {} not found in redis".format(ca_redis_key))
            return None

        ca_key = serialization.load_pem_private_key(ca.get("k"), password=None)
        cert_authority = x509.load_pem_x509_certificate(ca.get("c"))

        # Generate new RSA key
        client_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )

        # Build subject name
        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, username),
            ]
        )

        # Build the certificate
        now = datetime.now(timezone.utc)
        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(cert_authority.subject)
            .public_key(client_key.public_key())
            .serial_number(random.randint(0, 100000000))
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=365) - timedelta(seconds=1))
        )

        # Add extensions
        builder = builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        builder = builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        client_ca_key_identifier = cert_authority.extensions.get_extension_for_class(
            x509.SubjectKeyIdentifier
        )
        builder = builder.add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(
                client_ca_key_identifier.value
            ),
            critical=False,
        )

        if is_server_cert:
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=True,
            )
        else:
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
                critical=True,
            )

        if ip:
            san_entries = [
                x509.IPAddress(IPv4Address(str(ip))),
                x509.DNSName("kubernetes"),
                x509.DNSName("kubernetes.default"),
                x509.DNSName("kubernetes.default.svc"),
                x509.DNSName("kubernetes.default.svc.cluster"),
                x509.DNSName("kubernetes.svc.cluster.local"),
            ]
            builder = builder.add_extension(
                x509.SubjectAlternativeName(san_entries),
                critical=False,
            )

        # Sign the certificate
        certificate = builder.sign(ca_key, hashes.SHA256())

        # Serialize to PEM
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
        key_pem = client_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        return {
            "f": mTLS._get_digest(cert_pem),
            "c": cert_pem,
            "k": key_pem,
        }

    @staticmethod
    def generate_new_ca(username) -> KubeCerts:
        # Generate new RSA key
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )

        # Build subject/issuer name (self-signed, so they're the same)
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, username),
            ]
        )

        # Build the certificate
        now = datetime.now(timezone.utc)
        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(ca_key.public_key())
            .serial_number(random.randint(0, 100000000))
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=10 * 365) - timedelta(seconds=1))
        )

        # Add extensions
        builder = builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=0),
            critical=True,
        )
        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        )
        builder = builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=False,
        )

        # Sign the certificate (self-signed)
        certificate = builder.sign(ca_key, hashes.SHA256())

        # Serialize to PEM
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
        key_pem = ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        return {
            "f": mTLS._get_digest(cert_pem),
            "c": cert_pem,
            "k": key_pem,
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

        # Build CertificateOptions with explicit settings for mTLS
        server_cert = certs[server_cert_redis_key]
        client_ca = certs[client_ca_redis_key]

        ctx = CertificateOptions(
            privateKey=server_cert.privateKey.original,
            certificate=server_cert.original,
            caCerts=[client_ca.original],
            verify=True,
            requireCertificate=True,
            acceptableProtocols=[b"http/1.1"],  # ALPN support
        )

        # Explicitly add the client CA to the list sent to clients during handshake
        # This tells clients which CA their certificate should be signed by
        ssl_ctx = ctx.getContext()
        ssl_ctx.add_client_ca(client_ca.original)

        return ctx
