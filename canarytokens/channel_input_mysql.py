import struct
from typing import Tuple

from twisted.application import internet
from twisted.internet.protocol import Factory, Protocol
from twisted.logger import Logger

from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import InputChannel
from canarytokens.constants import INPUT_CHANNEL_MYSQL
from canarytokens.exceptions import NoCanarytokenFound, NoCanarytokenPresent
from canarytokens.models import AdditionalInfo, MySQLTokenHit, TokenTypes
from canarytokens.queries import get_canarydrop
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

log = Logger()

MYSQL_RSP = b"\x5b\x00\x00\x00\x0a\x38\x2e\x30\x2e\x32\x36\x2d\x30\x75\x62\x75\x6e\x74\x75\x30\x2e\x32\x30\x2e\x30\x34\x2e\x32\x00\x13\x00\x00\x00\x14\x37\x06\x5c\x3c\x26\x2a\x01\x00\xff\xf7\xff\x02\x00\xff\xcf\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x50\x3c\x16\x61\x26\x60\x49\x4f\x4b\x6d\x7a\x37\x00\x63\x61\x63\x68\x69\x6e\x67\x5f\x73\x68\x61\x32\x5f\x70\x61\x73\x73\x77\x6f\x72\x64\x00"
MIN_LENGTH = 60


class CanaryMySQLProtocol(Protocol):
    def __init__(self):
        self.buf = b""

    def connectionMade(self):
        log.info("mysql connection made!")
        self.transport.write(MYSQL_RSP)

    def dataReceived(self, data: bytes) -> None:
        log.debug("mysql data: {}", data=data)
        self.buf += data
        if len(self.buf) < MIN_LENGTH:
            return
        peer = self.transport.getPeer()
        src_host: str = peer.host
        try:
            canarydrop, hit = self.handleQuery(src_host, self.buf)
            self.factory.dispatch(canarydrop=canarydrop, token_hit=hit)
        except (ValueError, NoCanarytokenFound, NoCanarytokenPresent) as e:
            log.info(f"{e}")
        except Exception as e:
            log.error(f"Error in MySQL channel: {e} | Data received: {data}")
        self.transport.loseConnection()

    @staticmethod
    def handleQuery(src_host: str, buf: bytes) -> Tuple[Canarydrop, MySQLTokenHit]:
        try:
            capability_flags, max_packet_sz, char_set, username = struct.Struct(
                "!4s4sc27x25s"
            ).unpack_from(buf)
        except struct.error:
            raise ValueError("Failed to decode MySQL query.")

        log.info(f"MySQL Query from {src_host}: {username}")
        token = Canarytoken(value=username)
        canarydrop = get_canarydrop(canarytoken=token)

        try:
            additional_info = CanaryMySQLProtocol.additionalInfo(buf)
        except Exception as e:
            log.failure(f"Error getting additional info: {e} from buf: {buf}")
            additional_info = AdditionalInfo()

        hit: MySQLTokenHit = token.create_token_hit(
            token_type=TokenTypes.MY_SQL,
            input_channel=INPUT_CHANNEL_MYSQL,
            src_ip=src_host,
            hit_info={"additional_info": additional_info.dict()},
        )
        canarydrop.add_canarydrop_hit(token_hit=hit)

        return canarydrop, hit

    @staticmethod
    def additionalInfo(buf: bytes) -> AdditionalInfo:
        start_of_locale = MIN_LENGTH + 1
        end_of_locale = start_of_locale + 4
        if len(buf) <= end_of_locale + 1:
            return AdditionalInfo()
        locale = buf[start_of_locale : end_of_locale + 1].decode()  # noqa: E203
        host_buf = buf[end_of_locale + 1 :]  # noqa: E203
        if b"\x00" in host_buf:
            host_buf = host_buf[: host_buf.index(b"\x00")]
        hostname = host_buf.decode()
        return AdditionalInfo(mysql_client={"hostname": [hostname], "locale": [locale]})


class CanaryMySQLFactory(InputChannel, Factory):
    protocol = CanaryMySQLProtocol
    CHANNEL = INPUT_CHANNEL_MYSQL

    def __init__(
        self,
        switchboard: Switchboard,
        switchboard_scheme: str,
        switchboard_hostname: str,
    ):
        InputChannel.__init__(
            self,
            switchboard=switchboard,
            switchboard_scheme=switchboard_scheme,
            switchboard_hostname=switchboard_hostname,
            name=self.CHANNEL,
        )


class ChannelMySQL:
    def __init__(
        self,
        port: int,
        switchboard: Switchboard,
        switchboard_scheme: str,
        switchboard_hostname: str,
    ):
        self.service = internet.TCPServer(
            port,
            CanaryMySQLFactory(
                switchboard=switchboard,
                switchboard_scheme=switchboard_scheme,
                switchboard_hostname=switchboard_hostname,
            ),
        )
