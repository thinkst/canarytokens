import base64
import json
from ipaddress import IPv4Address

import pytest
from OpenSSL.crypto import FILETYPE_PEM, load_certificate, load_privatekey
from twisted.internet.ssl import CertificateOptions

from canarytokens import canarydrop as cd
from canarytokens import kubeconfig
from canarytokens import kubeconfig as kc
from canarytokens import queries, tokens
from canarytokens.channel_input_mtls import (
    ChannelKubeConfig,
    ChirpData,
    mTLS,
    mTLSFactory,
)
from canarytokens.constants import CANARYTOKEN_ALPHABET
from canarytokens.exceptions import NoCanarytokenFound
from canarytokens.kubeconfig import KubeConfig, get_kubeconfig
from canarytokens.models import TokenTypes
from canarytokens.queries import save_certificate
from canarytokens.settings import BackendSettings, Settings
from canarytokens.switchboard import Switchboard


def test_kubeconfig_mtls_create_and_save_cert(setup_db):
    """Create and load a `KubeConfig` and check that
    the returned token and config are of the correct shape.
    """
    client_ca_redis_key = kubeconfig.ClientCA
    ca = mTLS.generate_new_ca(
        username="kubernetes-ca",
    )
    save_certificate(client_ca_redis_key, ca)
    token, base64config = get_kubeconfig()
    config_file = base64.b64decode(base64config)
    assert len(token) == 25
    assert all(o in CANARYTOKEN_ALPHABET for o in token)

    # Check key is decode able and valid:
    config_file_lines = config_file.splitlines()
    client_certificate_data = base64.b64decode(
        config_file_lines[10].split(b"client-certificate-data:")[-1].strip()
    )
    client_key_data = base64.b64decode(
        config_file_lines[11].split(b"client-key-data:")[-1].strip()
    )

    cert_authority = load_certificate(FILETYPE_PEM, client_certificate_data)
    assert cert_authority.get_issuer().CN == "kubernetes-ca"
    ca_key = load_privatekey(FILETYPE_PEM, client_key_data)
    assert ca_key.check()
    assert len(config_file.splitlines()) == 18


def test_channel_mtls_ssl_context(setup_db):
    ssl_context = ChannelKubeConfig._get_ssl_context(
        client_ca_redis_key=kubeconfig.ClientCA,
        server_ca_redis_key=kubeconfig.ServerCA,
        server_cert_redis_key=kubeconfig.ServerCert,
        ip="127.0.0.1",
    )
    assert isinstance(ssl_context, CertificateOptions)


def test_mtls_factory_revieve_lines(
    backend_settings: BackendSettings, settings: Settings, setup_db
):
    """
    Test the mTLSFactory and its protocol:mTLS can receive lines and dispatch a `chirp`.
    Note: Dispatch is tested in integration tests.
    This test asserts that hits were created.
    """
    token_value, kube_config = kubeconfig.get_kubeconfig()
    canarytoken = tokens.Canarytoken(value=token_value)
    canarydrop = cd.Canarydrop(
        generate=True,
        type=TokenTypes.KUBECONFIG,
        alert_email_enabled=True,
        alert_email_recipient="test@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="test",
        browser_scanner_enabled=False,
        kubeconfig=kube_config,
    )
    queries.save_canarydrop(canarydrop)
    switchboard = Switchboard()
    kuc = kubeconfig.KubeConfig(
        client_ca_redis_key=kc.ClientCA,
        server_ca_redis_key=kc.ServerCA,
        server_endpoint_ip="127.0.0.1",
        server_endpoint_port=settings.CHANNEL_MTLS_KUBECONFIG_PORT,
    )
    mtls_factory = mTLSFactory(
        headers=kuc.kc_headers,
        bodies=kuc.bodies,
        channel_name="mTLS",
        enricher=None,
        backend_scheme=backend_settings.BACKEND_SCHEME,
        backend_hostname=backend_settings.BACKEND_HOSTNAME,
        switchboard=switchboard,
    )
    mtls = mtls_factory.buildProtocol("127.0.0.1")
    from twisted.test import proto_helpers

    proto_helpers.StringTransport()
    mtls.makeConnection(proto_helpers.StringTransport())
    with open("tests/data/kubeconfig_lines.txt", mode="r") as fp:
        lines = fp.readlines()
    for line in lines:
        mtls.lineReceived(line.strip().encode())
    mtls.send_response()
    with open("tests/data/kubeconfig_chirp.json") as fp:
        data = json.load(fp=fp)
    # chirp_data = {k:v if isinstance(v, bytes) else v.encode() for k, v in data.items()}
    chirp_data: ChirpData = {
        "f": data["f"].encode(),
        "tf": canarydrop.canarytoken.value().encode(),
        "location": data["location"],
        "useragent": data["useragent"],
        "ip": data["ip"],
    }
    mtls.chirp(trigger=chirp_data)
    updated_drop = queries.get_canarydrop(canarytoken=canarydrop.canarytoken)
    assert len(updated_drop.triggered_details.hits) == 1
    assert updated_drop.triggered_details.hits[0].geo_info.ip == chirp_data["ip"]

    with pytest.raises(NoCanarytokenFound):
        chirp_data["tf"] = b"thisisnotavalidtoken"
        mtls.chirp(trigger=chirp_data)


def test_ChannelKubeConfig(backend_settings, settings: Settings, setup_db):
    switchboard = Switchboard()
    kube_channel = ChannelKubeConfig(
        backend_settings=backend_settings,
        switchboard_settings=settings,
        switchboard=switchboard,
    )
    assert kube_channel.port == settings.CHANNEL_MTLS_KUBECONFIG_PORT
    assert kube_channel.ip == IPv4Address(settings.PUBLIC_IP)


def test_header_generation():
    headers = KubeConfig.kc_headers()
    assert isinstance(headers, bytes)
    assert len(headers.splitlines()) == 5
