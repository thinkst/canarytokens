from canarytokens.channel_input_wireguard import ChannelWireGuard, WireGuardProtocol
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.switchboard import Switchboard

switchboard = Switchboard()


def test_wireguard_channel(
    frontend_settings: FrontendSettings, settings: SwitchboardSettings
):
    """
    Creates a Wireguard Channel and passes it data with an invalid timestamp
    """

    canarytokens_wireguard = ChannelWireGuard(
        port=settings.CHANNEL_WIREGUARD_PORT,
        switchboard=switchboard,
        switchboard_scheme=settings.SWITCHBOARD_SCHEME,
        switchboard_hostname=frontend_settings.DOMAINS[0],
        switchboard_settings=settings,
    )
    wireguard_protocol: WireGuardProtocol = canarytokens_wireguard.service.args[1]
    data = b"b'\x01\x00\x00\x00\xeb\x9d\x17P\xf8_r\x96\x0e\xf6Ven\x8d\x07mE,\xb3\xe3\xd1\x05\xd1\x02\xd4\xf2Fq=\xa0\xee\xb3\xc9\xc4\xee\x18\xcc\xf0D6\xa6\x06)p:K\xe4X\x10F\xa0\xc9\x08H\xc3\x9f\xa8Y\x93:\x0b3n\x95j\xc3k\xe6T\xbdR\xcc\xae\x91\x87\xb7\x1dX\xb9&\xbdqD\xd7!\xff\x13\xca\xe8\xbc$\xc4#\x1ey|\x15\xe4\xf0|3\xa9\xdd\xa4\xf0\xf5\x94\x97}\x1c\xd7\x01\xba\xc8|?Y\xdf\x9a\x19p\xef\x10\x03\xbf\x13i\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'"
    wireguard_protocol.datagramReceived(
        data=data, src=("172.20.0.1", settings.CHANNEL_WIREGUARD_PORT)
    )
