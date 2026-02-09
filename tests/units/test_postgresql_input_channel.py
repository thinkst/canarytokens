import os
import struct

import pytest
from twisted.internet.testing import StringTransport

from canarytokens.canarydrop import Canarydrop
from canarytokens.channel_input_postgresql import ChannelPostgreSQL
from canarytokens.models import TokenTypes
from canarytokens.postgresql import (
    MSG_AUTH,
    MSG_ERROR_RESPONSE,
    AUTH_MD5_PASSWORD,
    PROTOCOL_VERSION,
    SSL_REQUEST_CODE,
    PostgreSQLProtocol,
    compute_md5_inner_hash,
    compute_md5_response,
)
from canarytokens.queries import (
    get_canarydrop_triggered_details,
    postgresql_passwordmap_add,
    save_canarydrop,
)
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken
from canarytokens.utils import strtobool

switchboard = Switchboard()


def build_startup_message(username: str, database: str = "", **extra_params) -> bytes:
    if not database:
        database = username
    params = b""
    for key, value in [
        ("user", username),
        ("database", database),
        *extra_params.items(),
    ]:
        params += key.encode() + b"\x00" + value.encode() + b"\x00"
    params += b"\x00"
    length = 4 + 4 + len(params)
    return struct.pack("!II", length, PROTOCOL_VERSION) + params


def build_ssl_request() -> bytes:
    return struct.pack("!II", 8, SSL_REQUEST_CODE)


def build_password_message(password_hash: str) -> bytes:
    payload = password_hash.encode() + b"\x00"
    msg_len = 4 + len(payload)
    return bytes([ord("p")]) + struct.pack("!I", msg_len) + payload


def test_md5_hash_functions():
    inner_hash = compute_md5_inner_hash("secret", "postgres")
    assert len(inner_hash) == 32
    assert inner_hash == compute_md5_inner_hash("secret", "postgres")
    assert inner_hash != compute_md5_inner_hash("secret", "other_user")

    salt = b"\x01\x02\x03\x04"
    response = compute_md5_response(inner_hash, salt)
    assert response.startswith("md5")
    assert len(response) == 35
    assert response == compute_md5_response(inner_hash, salt)
    assert response != compute_md5_response(inner_hash, b"\x05\x06\x07\x08")


def test_protocol_ssl_negotiation():
    protocol = PostgreSQLProtocol(channel=None)
    protocol.transport = StringTransport()
    protocol.makeConnection(protocol.transport)

    protocol.dataReceived(build_ssl_request())
    assert protocol.transport.value() == b"N"
    assert protocol._state == "startup"


def test_protocol_startup_and_md5_challenge():
    protocol = PostgreSQLProtocol(channel=None)
    protocol.transport = StringTransport()
    protocol.makeConnection(protocol.transport)

    startup = build_startup_message(
        "postgres", "mydb", application_name="psql", client_encoding="UTF8"
    )
    protocol.dataReceived(startup)

    assert protocol._username == "postgres"
    assert protocol._database == "mydb"
    assert protocol._client_params == {
        "application_name": "psql",
        "client_encoding": "UTF8",
    }
    assert protocol._state == "wait_password"

    response = protocol.transport.value()
    assert len(response) == 13
    assert response[0] == MSG_AUTH
    auth_type = struct.unpack("!I", response[5:9])[0]
    assert auth_type == AUTH_MD5_PASSWORD
    assert len(protocol._salt) == 4


def test_protocol_ssl_then_startup():
    protocol = PostgreSQLProtocol(channel=None)
    protocol.transport = StringTransport()
    protocol.makeConnection(protocol.transport)

    protocol.dataReceived(build_ssl_request())
    assert protocol.transport.value() == b"N"
    protocol.transport.clear()

    protocol.dataReceived(build_startup_message("admin"))
    assert protocol._username == "admin"
    assert protocol._state == "wait_password"

    response = protocol.transport.value()
    assert response[0] == MSG_AUTH


class FakeChannel:
    def __init__(self):
        self.auth_calls = []

    def handle_auth(self, **kwargs):
        self.auth_calls.append(kwargs)


def test_protocol_full_auth_flow():
    channel = FakeChannel()
    protocol = PostgreSQLProtocol(channel=channel)
    protocol.transport = StringTransport()
    protocol.makeConnection(protocol.transport)

    protocol.dataReceived(build_startup_message("postgres", "mydb"))
    protocol.transport.clear()

    salt = protocol._salt
    inner_hash = compute_md5_inner_hash("secret", "postgres")
    client_hash = compute_md5_response(inner_hash, salt)
    protocol.dataReceived(build_password_message(client_hash))

    assert len(channel.auth_calls) == 1
    call = channel.auth_calls[0]
    assert call["username"] == "postgres"
    assert call["database"] == "mydb"
    assert call["client_hash"] == client_hash
    assert call["salt"] == salt
    assert call["client_params"] == {}


def test_protocol_deny_sends_error():
    protocol = PostgreSQLProtocol(channel=None)
    protocol.transport = StringTransport()
    protocol.makeConnection(protocol.transport)
    protocol._username = "postgres"

    protocol.deny()

    response = protocol.transport.value()
    assert response[0] == MSG_ERROR_RESPONSE
    assert b"28P01" in response
    assert b"password authentication failed" in response
    assert protocol.transport.disconnecting


def test_postgresql_channel(frontend_settings, settings):
    """
    Creates a PostgreSQL Channel and checks that it sends the MD5 challenge
    and denies access for an unknown token.
    """
    canarytokens_pg = ChannelPostgreSQL(
        port=settings.CHANNEL_POSTGRESQL_PORT,
        switchboard=switchboard,
        switchboard_scheme=settings.SWITCHBOARD_SCHEME,
        switchboard_hostname=frontend_settings.DOMAINS[0],
    )
    pg_factory = canarytokens_pg.service.args[1]
    protocol: PostgreSQLProtocol = pg_factory.buildProtocol(addr="1.0.0.1")
    protocol.transport = StringTransport()
    protocol.makeConnection(protocol.transport)

    protocol.dataReceived(build_startup_message("postgres"))

    response = protocol.transport.value()
    assert len(response) == 13
    assert response[0] == MSG_AUTH
    auth_type = struct.unpack("!I", response[5:9])[0]
    assert auth_type == AUTH_MD5_PASSWORD


@pytest.mark.skipif(
    not strtobool(os.getenv("LIVE", "False")), reason="Only test on live system"
)
def test_postgresql_handle_auth(setup_db):
    token = Canarytoken()
    drop = Canarydrop(
        canarytoken=token,
        type=TokenTypes.POSTGRESQL,
        memo="test PostgreSQL handle_auth",
        postgresql_username="postgres",
        postgresql_password="secret",
        postgresql_server="127.0.0.1",
        postgresql_port=5432,
    )
    save_canarydrop(drop)

    inner_hash = compute_md5_inner_hash("secret", "postgres")
    postgresql_passwordmap_add(inner_hash, token.value())

    salt = b"\x01\x02\x03\x04"
    client_hash = compute_md5_response(inner_hash, salt)

    canarytokens_pg = ChannelPostgreSQL(
        port=15432,
        switchboard=switchboard,
        switchboard_scheme="http",
        switchboard_hostname="127.0.0.1",
    )
    pg_factory = canarytokens_pg.service.args[1]
    protocol: PostgreSQLProtocol = pg_factory.buildProtocol(addr="172.20.0.3")
    protocol.transport = StringTransport()
    protocol.makeConnection(protocol.transport)

    protocol.dataReceived(build_startup_message("postgres", "mydb"))
    protocol.transport.clear()
    protocol._salt = salt

    protocol.dataReceived(build_password_message(client_hash))

    history = get_canarydrop_triggered_details(token)
    assert len(history.hits) == 1
    assert history.hits[0].postgresql_username == "postgres"
    assert history.hits[0].additional_info is not None
    assert "Database" in history.hits[0].additional_info.postgresql_log_data
