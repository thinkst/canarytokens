import struct

import pytest
from twisted.internet.testing import StringTransport

from canarytokens.canarydrop import Canarydrop
from canarytokens.channel_input_mysql import (
    MYSQL_RSP,
    CanaryMySQLProtocol,
    ChannelMySQL,
)
from canarytokens.models import AdditionalInfo, TokenTypes
from canarytokens.queries import get_canarydrop_triggered_details, save_canarydrop
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

switchboard = Switchboard()


@pytest.mark.parametrize(
    "buf, expected_additional_info",
    [
        (
            b")\x01\x00\x01\x85\xa2\xb8\x99\xa3\x10\x00@\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x007tbv2sulcj23hxprg05z8a4mfen_USf997602984b1\x00 \x82\xb5\xdc\xd3a\xc25>\r#\xfe\x818i\x8a\xea\xcd\xa0\xe1{\x1a\x03@\x02\xf1\xba\xb6\xecu\xd5\xf9\x96caching_sha2_password\x00\xa6\t_platform\x06x86_64\x03_os\x05Linux\x0c_client_name\x08libmysql _client_replication_channel_name\x00\x04_pid\x011\x0c_client_role\x13binary_log_listener\x0f_client_version\x068.0.29\x0cprogram_name\x06mysqld",
            AdditionalInfo(
                mysql_client={"hostname": ["f997602984b1"], "locale": ["en_US"]}
            ),
        ),
        (
            b")\x01\x00\x01\x85\xa2\xb8\x99\xa3\x10\x00@\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x007tbv2sulcj23hxprg05z8a4mf",
            AdditionalInfo(**{}),
        ),
        (
            b")\x01\x00\x01\x85\xa2\xb8\x99\xa3\x10\x00@\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x007tbv2sulcj23hxprg05z8a4mfen_USf9976 \xe9 02984b1\x00 \x82\xb5\xdc\xd3a\xc25>\r#\xfe\x818i\x8a\xea\xcd\xa0\xe1{\x1a\x03@\x02\xf1\xba\xb6\xecu\xd5\xf9\x96caching_sha2_password\x00\xa6\t_platform\x06x86_64\x03_os\x05Linux\x0c_client_name\x08libmysql _client_replication_channel_name\x00\x04_pid\x011\x0c_client_role\x13binary_log_listener\x0f_client_version\x068.0.29\x0cprogram_name\x06mysqld",
            AdditionalInfo(**{}),
        ),
    ],
)
def test_mysql_additionalInfo(buf, expected_additional_info):
    """Check that additionalInfo extracts hostname and locale"""

    additional_info = CanaryMySQLProtocol.additionalInfo(buf)
    assert additional_info.dict() == expected_additional_info.dict()


def test_mysql_handleQuery(setup_db):
    token = Canarytoken()
    drop = Canarydrop(
        canarytoken=token, type=TokenTypes.MY_SQL, memo="test MySQL handleQuery"
    )
    save_canarydrop(drop)
    buf = b""

    capability_flags, max_packet_sz, char_set = (
        b")\x01\x00\x01",
        b"\x85\xa2\xb8\x99",
        b"\xa3",
    )

    buf += struct.Struct("!4s4sc27x25s").pack(
        capability_flags, max_packet_sz, char_set, token.value().encode()
    )

    locale = b"en_US"
    hostname = b"f997602984b1"
    buf += locale + hostname

    buf += b"\x00 \x82\xb5\xdc\xd3a\xc25>\r#\xfe\x818i\x8a\xea\xcd\xa0\xe1{\x1a\x03@\x02\xf1\xba\xb6\xecu\xd5\xf9\x96caching_sha2_password\x00\xa6\t_platform\x06x86_64\x03_os\x05Linux\x0c_client_name\x08libmysql _client_replication_channel_name\x00\x04_pid\x011\x0c_client_role\x13binary_log_listener\x0f_client_version\x068.0.29\x0cprogram_name\x06mysqld"

    src_host = "172.20.0.3"

    ret_drop, ret_hit = CanaryMySQLProtocol.handleQuery(src_host, buf)
    assert ret_drop.canarytoken == drop.canarytoken

    history = get_canarydrop_triggered_details(token)
    assert len(history.hits) == 1
    assert ret_hit.dict() == history.hits[0].dict()


def test_mysql_channel(backend_settings, settings):
    """
    Creates a MySQL Channel and checks that it returns the expected response when we connect to it.

    We make a token to construct the query, but *don't* save it to redis as this is tested elsewhere and we want to hit the error.
    """
    token = Canarytoken()
    buf = b""

    capability_flags, max_packet_sz, char_set = (
        b")\x01\x00\x01",
        b"\x85\xa2\xb8\x99",
        b"\xa3",
    )

    buf += struct.Struct("!4s4sc27x25s").pack(
        capability_flags, max_packet_sz, char_set, token.value().encode()
    )

    locale = b"en_US"
    hostname = b"f997602984b1"
    buf += locale + hostname

    buf += b"\x00 \x82\xb5\xdc\xd3a\xc25>\r#\xfe\x818i\x8a\xea\xcd\xa0\xe1{\x1a\x03@\x02\xf1\xba\xb6\xecu\xd5\xf9\x96caching_sha2_password\x00\xa6\t_platform\x06x86_64\x03_os\x05Linux\x0c_client_name\x08libmysql _client_replication_channel_name\x00\x04_pid\x011\x0c_client_role\x13binary_log_listener\x0f_client_version\x068.0.29\x0cprogram_name\x06mysqld"

    canarytokens_mysql = ChannelMySQL(
        port=settings.CHANNEL_MYSQL_PORT,
        switchboard=switchboard,
        backend_scheme=backend_settings.BACKEND_SCHEME,
        backend_hostname=backend_settings.BACKEND_HOSTNAME,
    )
    mysql_factory = canarytokens_mysql.service.args[1]
    protocol: CanaryMySQLProtocol = mysql_factory.buildProtocol(addr="1.0.0.1")
    mysql_factory.protocol = protocol
    mysql_factory.protocol.transport = StringTransport()
    mysql_factory.protocol.makeConnection(mysql_factory.protocol.transport)
    mysql_factory.protocol.dataReceived(b"")
    mysql_factory.protocol.dataReceived(buf)

    assert MYSQL_RSP == mysql_factory.protocol.transport.value()

    mysql_factory.protocol.transport.clear()
