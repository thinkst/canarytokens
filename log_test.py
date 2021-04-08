import sys, os, io
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from twisted.names import dns, server
from caa_monkeypatch import monkey_patch_caa_support
monkey_patch_caa_support()
from twisted.application import service, internet
from twisted.logger import globalLogPublisher, textFileLogObserver
# from twisted.logger import Logger, globalLogPublisher, textFileLogObserver
# from twisted.logger import Logger, globalLogPublisher
# log = Logger()
# from twisted.python import logfile
from loghandlers import webhookLogObserver
import settings
from channel_dns import DNSServerFactory, ChannelDNS
from channel_http import ChannelHTTP
# from channel_input_imgur import ChannelImgur
# from channel_input_linkedin import ChannelLinkedIn
# from channel_input_bitcoin import ChannelBitcoin
# from channel_input_smtp import ChannelSMTP
from channel_output_email import EmailOutputChannel
# from channel_output_twilio import TwilioOutputChannel
# from channel_output_webhook import WebhookOutputChannel
from switchboard import Switchboard

from queries import update_tor_exit_nodes_loop


application = service.Application("Canarydrops Switchboard")

# f = logfile.LogFile.fromFullPath('/tmp/twistedLogTest', rotateLength=500000000,
#                                  maxRotatedFiles=20)
# globalLogPublisher.addObserver(textFileLogObserver(f))
# globalLogPublisher.addObserver(textFileLogObserver(io.open("/tmp/log-1.json", "a")))
#######
# works but dubs:
globalLogPublisher.addObserver(textFileLogObserver(io.open("/tmp/log-1.json", "a")))
# globalLogPublisher.addObserver(jsonFileLogObserver(io.open("/tmp/log-1.json", "a")))
globalLogPublisher.addObserver(webhookLogObserver())
import pudb; pudb.set_trace()
####### ends works part commented
# globalLogBeginner.beginLoggingTo([textFileLogObserver(io.open("/tmp/log-1.json", "a")),webhookLogObserver()])
# globalLogBeginner.beginLoggingTo(webhookLogObserver())


# log.info('Canarydrops switchboard started')
# log.error('Testing error message first')
# log.critical('Testing critical message first')
# log.error('Testing error message')
# log.critical('Testing critical message')
# log.msg('Canarydrops switchboard started')

switchboard = Switchboard()

email_output_channel  = EmailOutputChannel(switchboard=switchboard)
# twilio_output_channel = TwilioOutputChannel(switchboard=switchboard)
# webhook_output_channel = WebhookOutputChannel(switchboard=switchboard)

dns_service = service.MultiService()

factory = DNSServerFactory(
    clients=[ChannelDNS(listen_domain=settings.LISTEN_DOMAIN,
                        switchboard=switchboard)]
)
udp_factory = dns.DNSDatagramProtocol(factory)
internet.TCPServer(1053, factory)\
            .setServiceParent(dns_service)
internet.UDPServer(1053, udp_factory)\
            .setServiceParent(dns_service)
dns_service.setServiceParent(application)

canarytokens_httpd = ChannelHTTP(port=569,
                                switchboard=switchboard)
canarytokens_httpd.service.setServiceParent(application)

# canarytokens_imgur = ChannelImgur(min_delay=settings.CHANNEL_IMGUR_MIN_DELAY,
#                                  switchboard=switchboard)
# canarytokens_imgur.service.setServiceParent(application)

# canarytokens_linkedin = ChannelLinkedIn(min_delay=settings.CHANNEL_LINKEDIN_MIN_DELAY,
#                                  switchboard=switchboard)
# canarytokens_linkedin.service.setServiceParent(application)

# canarytokens_bitcoin = ChannelBitcoin(min_delay=settings.CHANNEL_BITCOIN_MIN_DELAY,
#                                  switchboard=switchboard)
# canarytokens_bitcoin.service.setServiceParent(application)

# canarytokens_smtp = ChannelSMTP(port=settings.CHANNEL_SMTP_PORT,
#                                  switchboard=switchboard)
# canarytokens_smtp.service.setServiceParent(application)


#loop to update tor exit nodes every 30 min
loop_http = internet.task.LoopingCall(update_tor_exit_nodes_loop)
loop_http.start(1800)

# log.error('Testing error message second')
# log.critical('Testing critical message second')
# log.error('Testing error message third')
# log.critical('Testing critical message third')
# log.error('Testing error message fourth')
# log.critical('Testing critical message fourth')
