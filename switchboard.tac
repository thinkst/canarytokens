import sys, os

from twisted.names import dns, server
from twisted.application import service, internet
from twisted.python import log

import settings
from channel_dns import DNSServerFactory, ChannelDNS
from channel_http import ChannelHTTP
from channel_input_imgur import ChannelImgur
from channel_input_linkedin import ChannelLinkedIn
from channel_input_bitcoin import ChannelBitcoin
from channel_input_smtp import ChannelSMTP
from channel_output_email import EmailOutputChannel
from channel_output_twilio import TwilioOutputChannel
from channel_output_webhook import WebhookOutputChannel
from switchboard import Switchboard

log.msg('Canarydrops switchboard started')

application = service.Application("Canarydrops Switchboard")

switchboard = Switchboard()

email_output_channel  = EmailOutputChannel(switchboard=switchboard)
twilio_output_channel = TwilioOutputChannel(switchboard=switchboard)
webhook_output_channel = WebhookOutputChannel(switchboard=switchboard)

dns_service = service.MultiService()

factory = DNSServerFactory(
    clients=[ChannelDNS(listen_domain=settings.LISTEN_DOMAIN,
                        switchboard=switchboard)]
)
udp_factory = dns.DNSDatagramProtocol(factory)
internet.TCPServer(settings.CHANNEL_DNS_PORT, factory)\
            .setServiceParent(dns_service)
internet.UDPServer(settings.CHANNEL_DNS_PORT, udp_factory)\
            .setServiceParent(dns_service)
dns_service.setServiceParent(application)

canarytokens_httpd = ChannelHTTP(port=settings.CHANNEL_HTTP_PORT,
                                switchboard=switchboard)
canarytokens_httpd.service.setServiceParent(application)

canarytokens_imgur = ChannelImgur(min_delay=settings.CHANNEL_IMGUR_MIN_DELAY,
                                 switchboard=switchboard)
canarytokens_imgur.service.setServiceParent(application)

canarytokens_linkedin = ChannelLinkedIn(min_delay=settings.CHANNEL_LINKEDIN_MIN_DELAY,
                                 switchboard=switchboard)
canarytokens_linkedin.service.setServiceParent(application)

canarytokens_bitcoin = ChannelBitcoin(min_delay=settings.CHANNEL_BITCOIN_MIN_DELAY,
                                 switchboard=switchboard)
canarytokens_bitcoin.service.setServiceParent(application)

canarytokens_smtp = ChannelSMTP(port=settings.CHANNEL_SMTP_PORT,
                                 switchboard=switchboard)
canarytokens_smtp.service.setServiceParent(application)
