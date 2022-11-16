from OpenSSL.crypto import FILETYPE_PEM, PKey, TYPE_RSA, X509, X509Extension, dump_certificate, dump_privatekey, load_certificate, load_privatekey
from twisted.internet.ssl import PrivateCertificate, Certificate
from twisted.internet import reactor, defer
from twisted.internet.protocol import Factory
from twisted.logger import Logger
from twisted.protocols import basic
from twisted.internet.error import CertificateError
from twisted.application.internet import SSLServer

from time import time
from math import ceil

from channel import InputChannel
from constants import INPUT_CHANNEL_MTLS

import json
import base64
import random

from tokens import Canarytoken
from canarydrop import Canarydrop
from exception import NoCanarytokenPresent, NoCanarytokenFound
from channel import InputChannel
from queries import get_canarydrop, get_certificate, save_certificate, save_kc_endpoint, get_kc_hits, save_kc_hit_for_aggregation

log = Logger()

class mTLS(basic.LineReceiver):
    def __init__(self, factory, headers, bodies, ca_cert_path, enricher=None):
        self.factory = factory
        self.headers = headers
        self.bodies = bodies
        self.client_ca_cert_path = ca_cert_path
        self.lines = []
        self.enricher = enricher

    def lineReceived(self, line):
        self.lines.append(line)
        if not line:
            self.send_response()

    def send_response(self):
        client = self.transport.getPeer()

        req_uri = self.lines[0].split(" ")[1]

        headers = {l.split(':')[0]:l.split(':')[1].strip() for l in self.lines[2:-1]}
        user_agent = headers.get('User-Agent', 'Unknown')

        try:
            peer_certificate = Certificate.peerFromTransport(self.transport)
            f = peer_certificate.digest()
            self.sendLine("HTTP/1.1 401 Unauthorized")
            self.sendLine(self.headers())
            self.sendLine("")
            self.transport.write(json.dumps(self.bodies['unauthorized']))
            self.transport.loseConnection()

            self.chirp({'f': f, 'tf': f.replace(":","")[:25].lower(), 'ip': client.host, 'useragent': user_agent, 'location': req_uri.split("?")[0]})

        except CertificateError as e:
            log.error("CertificateError Exception: {}".format(e))
            self.sendLine("HTTP/1.1 403 Forbidden")
            self.sendLine(self.headers())
            self.sendLine("")
            response = self.bodies['forbidden']
            response['message'] = response['message'].format(req_uri.split("?")[0])
            self.transport.write(json.dumps(response))
            self.transport.loseConnection()
        except Exception as e:
            log.error("Exception send_response: {}".format(e))
            self.sendLine("HTTP/1.1 400 Bad Request")
            self.sendLine(self.headers())
            self.sendLine("")
            self.transport.write(json.dumps(self.bodies['bad']))
            self.transport.loseConnection()

        d = defer.Deferred()
        d.callback("Success")
        return d

    def chirp(self, trigger):
        try:
            token = Canarytoken(value=trigger['tf'])
            self.canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))

            if self.enricher:
                self.enricher(trigger, self.canarydrop, self.factory.dispatch)
            else:
                self.factory.dispatch(
                    canarydrop=self.canarydrop,
                    src_ip=trigger['ip'],
                    useragent=trigger['useragent'],
                    location=trigger['location']
                )

        except (NoCanarytokenPresent, NoCanarytokenFound):
            log.warn('No token for {tf} | Cert: {f}'.format(tf=trigger['tf'], f=trigger['f']))
        except Exception as e:
            log.error("Exception in chirp: {}".format(e))

    @staticmethod
    def generate_new_certificate(ca_cert_path, username, is_ca_generation_request=False, ip=None):
        try:
            if not is_ca_generation_request:
                ca = get_certificate(ca_cert_path)
                if not ca:
                    log.warn("CA with key {} not found in redis".format(ca_cert_path))
                    return None

                ca_key = load_privatekey(FILETYPE_PEM, base64.b64decode(ca.get('k').encode('ascii')))
                cert_authority = load_certificate(FILETYPE_PEM, base64.b64decode(ca.get('c').encode('ascii')))

                client_key = PKey()
                client_key.generate_key(TYPE_RSA, 4096)

                x509 = X509()
                x509.set_version(2)
                x509.set_serial_number(random.randint(0,100000000))

                client_subj = x509.get_subject()
                client_subj.commonName = username

                ca_extension = X509Extension("basicConstraints", False, "CA:FALSE")
                key_usage = X509Extension("keyUsage", True, "digitalSignature")

                if username == 'kube-apiserver':
                    san_list = ['IP:{}'.format(ip), 'DNS:kubernetes', 'DNS:kubernetes.default', 'DNS:kubernetes.default.svc', 'DNS:kubernetes.default.svc.cluster', 'DNS:kubernetes.svc.cluster.local']
                    x509.add_extensions([
                        ca_extension,
                        X509Extension("subjectKeyIdentifier", False, "hash", subject=x509),
                        X509Extension("extendedKeyUsage", True, "clientAuth"),
                        X509Extension("subjectAltName", False, ', '.join(san_list).encode()),
                        key_usage
                    ])
                else:
                    x509.add_extensions([
                        ca_extension,
                        X509Extension("subjectKeyIdentifier", False, "hash", subject=x509),
                        X509Extension("extendedKeyUsage", True, "clientAuth"),
                        key_usage
                    ])

                x509.set_issuer(cert_authority.get_subject())
                x509.set_pubkey(client_key)
                x509.gmtime_adj_notBefore(0)
                # default certificate validity is 1 year
                x509.gmtime_adj_notAfter(1*365*24*60*60 - 1)
                x509.sign(ca_key, 'sha256')
            else:
                client_key = PKey()
                client_key.generate_key(TYPE_RSA, 4096)

                x509 = X509()
                x509.set_version(2)
                x509.set_serial_number(random.randint(0,100000000))

                client_subj = x509.get_subject()
                client_subj.commonName = username

                ca_extension = X509Extension("basicConstraints", True, "CA:TRUE, pathlen:0")
                key_usage = X509Extension("keyUsage", False, "cRLSign,digitalSignature,keyCertSign")

                x509.add_extensions([
                    ca_extension,
                    X509Extension("subjectKeyIdentifier", False, "hash", subject=x509),
                    X509Extension("extendedKeyUsage", True, "clientAuth"),
                    key_usage
                ])

                x509.set_issuer(client_subj)
                x509.set_pubkey(client_key)
                x509.gmtime_adj_notBefore(0)
                # default certificate validity is 10 years with kubeadm
                x509.gmtime_adj_notAfter(10*365*24*60*60 - 1)
                x509.sign(client_key, 'sha256')

            b64_cert = base64.b64encode(dump_certificate(FILETYPE_PEM, x509).encode('ascii')).decode('ascii')
            b64_key = base64.b64encode(dump_privatekey(FILETYPE_PEM, client_key).encode('ascii')).decode('ascii')

            return {"f": mTLS._get_digest(dump_certificate(FILETYPE_PEM, x509)), "c": b64_cert, "k": b64_key}

        except Exception as e:
            print "Exception: {}".format(e)
            return None

    @staticmethod
    def _get_digest(cert):
        from twisted.internet.ssl import Certificate
        return Certificate.loadPEM(cert).digest()

class mTLSFactory(Factory, InputChannel):
    CHANNEL = INPUT_CHANNEL_MTLS
    protocol = mTLS
    def __init__(self, headers, bodies, ca_cert_path, channel_name=None, enricher=None, *a, **kw):
        self.headers = headers
        self.bodies = bodies
        self.client_ca_cert_path = ca_cert_path
        self.enricher = enricher

        self.switchboard = kw.pop('switchboard')
        InputChannel.__init__(self, switchboard=self.switchboard,
                              name=channel_name if channel_name is not None else self.CHANNEL,
                              unique_channel=False)

    def buildProtocol(self, addr):
        return mTLS(
            factory = self,
            headers=self.headers,
            bodies=self.bodies,
            ca_cert_path=self.client_ca_cert_path,
            enricher=self.enricher
        )

class ChannelKubeConfig():
    def __init__(self, ip='127.0.0.1', port=6443, switchboard=None):
        import kubeconfig

        self.client_ca_cert_path = kubeconfig.ClientCA
        self.server_cert_path = "kubeconfig_server"
        self.port = port
        self.ip = ip
        self.channel_name = 'Kubeconfig'

        server_endpoint = "%s:%s" % (ip, port)
        save_kc_endpoint(server_endpoint)

        kc = kubeconfig.KubeConfig(ca_cert_path=self.client_ca_cert_path, server_endpoint=server_endpoint)
        factory = mTLSFactory(
            headers=kc.kc_headers,
            bodies=kc.bodies,
            ca_cert_path=self.client_ca_cert_path,
            channel_name=self.channel_name,
            enricher=None,
            switchboard=switchboard
        )

        self.service = SSLServer(port, factory, self._get_ssl_context())

    def _get_ssl_context(self):

        client_ca = get_certificate(self.client_ca_cert_path)
        if not client_ca:
            try:
                ca = mTLS.generate_new_certificate(is_ca_generation_request=True, ca_cert_path=self.client_ca_cert_path, username="kubernetes-ca")
                if ca is not None:
                    save_certificate(self.client_ca_cert_path, ca)
                    client_ca = ca
            except Exception as e:
                log.error("Exception: {}".format(e))
                raise e

        client_ca_pem = "{}\n{}".format(base64.b64decode(client_ca.get('c')), base64.b64decode(client_ca.get('k')))
        certificate_authority = Certificate.loadPEM(client_ca_pem)

        self.server_ca_cert_path = self.server_cert_path+"_ca"
        server_cert = get_certificate(self.server_cert_path)
        server_cert_ca = get_certificate(self.server_ca_cert_path)
        if not server_cert:
            try:
                if not server_cert_ca:
                    ca = mTLS.generate_new_certificate(is_ca_generation_request=True, ca_cert_path=self.server_ca_cert_path, username="kubernetes-ca")
                    if ca is not None:
                        save_certificate(self.server_ca_cert_path, ca)

                _server_cert = mTLS.generate_new_certificate(ca_cert_path=self.server_ca_cert_path, username="kube-apiserver", ip=self.ip)

                if _server_cert is not None:
                    save_certificate(self.server_cert_path, _server_cert)
                    server_cert = _server_cert
                else:
                    raise Exception("Server Certificate generation failed. Cert:{}".format(_server_cert))

            except Exception as e:
                log.error("Exception: {}".format(e))
                raise e

        server_cert_pem = "{}\n{}".format(base64.b64decode(server_cert.get('c')), base64.b64decode(server_cert.get('k')))
        server_cert = PrivateCertificate.loadPEM(server_cert_pem)

        return server_cert.options(certificate_authority)
