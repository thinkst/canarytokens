import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from twisted.names import dns, server
from caa_monkeypatch import monkey_patch_caa_support
monkey_patch_caa_support()


from twisted.application import service, internet
from loghandlers import webhookLogObserver

from twisted.logger import ILogObserver, textFileLogObserver, globalLogPublisher
from twisted.python import logfile
from twisted.logger import Logger
log = Logger()

import settings
from channel_dns import DNSServerFactory, ChannelDNS
from channel_http import ChannelHTTP
from channel_input_imgur import ChannelImgur
from channel_input_linkedin import ChannelLinkedIn
from channel_input_bitcoin import ChannelBitcoin
from channel_input_smtp import ChannelSMTP
from channel_input_mysql import ChannelMySQL
from channel_input_wireguard import ChannelWireGuard
from channel_output_email import EmailOutputChannel
from channel_output_twilio import TwilioOutputChannel
from channel_output_webhook import WebhookOutputChannel
from switchboard import Switchboard

from queries import update_tor_exit_nodes_loop

application = service.Application("Canarydrops Switchboard")

f = logfile.LogFile.fromFullPath(settings.LOG_FILE, rotateLength=settings.SWITCHBOARD_LOG_SIZE,
                                 maxRotatedFiles=settings.SWITCHBOARD_LOG_COUNT)
globalLogPublisher.addObserver(textFileLogObserver(f))

if getattr(settings, 'ERROR_LOG_WEBHOOK', None):
    # Only create this log observer if the config is setup for it.
    globalLogPublisher.addObserver(webhookLogObserver())

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

canarytokens_mysql = ChannelMySQL(port=settings.CHANNEL_MYSQL_PORT,
                                 switchboard=switchboard)
canarytokens_mysql.service.setServiceParent(application)

canarytokens_wireguard = ChannelWireGuard(switchboard=switchboard)
canarytokens_wireguard.service.setServiceParent(application)

#loop to update tor exit nodes every 30 min
loop_http = internet.task.LoopingCall(update_tor_exit_nodes_loop)
loop_http.start(1800)
