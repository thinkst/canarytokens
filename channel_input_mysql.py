from twisted.logger import Logger
from twisted.internet.protocol import Protocol, Factory
from twisted.application import internet

from channel import InputChannel
from tokens import Canarytoken
from canarydrop import Canarydrop
from queries import get_canarydrop
from exception import NoCanarytokenFound
from constants import INPUT_CHANNEL_MYSQL

import struct

log = Logger()

MYSQL_RSP = b'\x5b\x00\x00\x00\x0a\x38\x2e\x30\x2e\x32\x36\x2d\x30\x75\x62\x75\x6e\x74\x75\x30\x2e\x32\x30\x2e\x30\x34\x2e\x32\x00\x13\x00\x00\x00\x14\x37\x06\x5c\x3c\x26\x2a\x01\x00\xff\xf7\xff\x02\x00\xff\xcf\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x50\x3c\x16\x61\x26\x60\x49\x4f\x4b\x6d\x7a\x37\x00\x63\x61\x63\x68\x69\x6e\x67\x5f\x73\x68\x61\x32\x5f\x70\x61\x73\x73\x77\x6f\x72\x64\x00'
MIN_LENGTH = 60


class CanaryMySQLProtocol(Protocol):
    def __init__(self):
        self.buf = b''

    def connectionMade(self):
        self.transport.write(MYSQL_RSP)

    def dataReceived(self, data):
        try:
            self.buf += data
            if len(self.buf) < MIN_LENGTH:
                return
            self.handleQuery()
        except NoCanarytokenFound:
            pass
        except Exception as e:
            log.error('Error in MySQL channel: {} | Data received: {}'.format(e, data))
        self.transport.loseConnection()

    def handleQuery(self):
        peer = self.transport.getPeer()
        src_host = peer.host

        capability_flags, max_packet_sz, char_set, username = \
            struct.Struct("!4s4sc27x25s").unpack_from(self.buf)

        log.info('MySQL Query from {}'.format(src_host))

        additional_info = self.additionalInfo()
        self.factory.dispatch_alert(username, src_host, additional_info)

    def additionalInfo(self):
        try:
            start_of_locale = MIN_LENGTH + 1
            end_of_locale = start_of_locale + 4
            locale = self.buf[start_of_locale:end_of_locale + 1]

            hostname = ""
            for c in self.buf[end_of_locale + 1:]:
                if c == b'\x00':
                    break
                hostname += c
            return {"MySQL Client": {"Hostname": [hostname], "Locale": [locale]}}
        except Exception as e:
            log.error('Error getting additional info: {}'.format(e))
        return None


class CanaryMySQLFactory(Factory, InputChannel):
    protocol = CanaryMySQLProtocol
    CHANNEL = INPUT_CHANNEL_MYSQL

    def __init__(self, switchboard=None):
        InputChannel.__init__(self, switchboard=switchboard, name=self.CHANNEL)

    def dispatch_alert(self, username, src_host, additional_info):
        token = Canarytoken(value=username)
        canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))
        self.dispatch(canarydrop=canarydrop, src_ip=src_host, additional_info=additional_info)

    def format_additional_data(self, **kwargs):
        additional_report = ''
        if kwargs.has_key('Hostname') and kwargs['Hostname']:
            additional_report += 'Hostname: {hostname}\r\n'.format(
                                                hostname=kwargs['Hostname'])
        if kwargs.has_key('Locale') and kwargs['Locale']:
            additional_report += 'Locale: {locale}\r\n'.format(
                                                locale=kwargs['Locale'])
        return additional_report


class ChannelMySQL():
    def __init__(self, port=3306, switchboard=None):
        self.service = internet.TCPServer(
            port, CanaryMySQLFactory(switchboard=switchboard))