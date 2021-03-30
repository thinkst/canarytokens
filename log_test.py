
# from twisted.application import service
from loghandlers import errorsToSlackLogObserver
# from twisted.application import internet
# from twisted.python import log # Old depracted, but used in switchboard
# from twisted.logger import ILogObserver, textFileLogObserver
# from twisted.python import logfile
# from twisted.web import  resource
# import pudb; pudb.set_trace()
# log.msg('testing switchboard started')
# application = service.Application("testing Canarydrops Switchboard")

# f = logfile.LogFile.fromFullPath('/tmp/twistedLogTest', rotateLength=500000000,
#                                  maxRotatedFiles=20)
# application.setComponent(ILogObserver, textFileLogObserver(f))
# application.setComponent(ILogObserver, errorsToSlackLogObserver)
# # import pudb; pudb.set_trace()
# log.err('testing switchboard started err')

# class Channel(object):
#     CHANNEL = 'Base'

#     def __init__(self, switchboard=None, name=None):
#         log.err('Channel Init')
#         self.switchboard = switchboard
#         self.name = name or self.CHANNEL
#         log.msg('Started channel {name}'.format(name=self.name))

# class InputChannel(Channel):
#     CHANNEL = 'InputChannel'

#     def __init__(self, switchboard=None, name=None, unique_channel=False):
#         log.err('InputChannel Init')
#         super(InputChannel, self).__init__(switchboard=switchboard,
#                                             name=name)

# class CanarytokenPage(resource.Resource, InputChannel):
#     def __init__(self, switchboard=None):
#         log.err('CanarytokenPage Init')


# class ChannelTester():
#     def __init__(self, port=80, switchboard=None):
#         log.err('ChannelTester Init')
#         canarytoken_page = CanarytokenPage()
#         self.service = internet.TCPServer(port)
#         # self.service=None
#         return None

# canarytokens_testing = ChannelTester()
# canarytokens_testing.service.setServiceParent(application)

import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from twisted.names import dns, server
from caa_monkeypatch import monkey_patch_caa_support
monkey_patch_caa_support()
# import logging
# # import logging.handlers
# from loghandlers import slack_handler

# logger = logging.getLogger('canary-tokens')
# try:
#     logger.addHandler(loghandlers.slack_handler())
# except SlackException as e:
#     logger.exception(e)

from twisted.application import service, internet
from twisted.python import log
from twisted.logger import ILogObserver, textFileLogObserver
from twisted.python import logfile

# import settings
# from channel_dns import DNSServerFactory, ChannelDNS
from channel_http import ChannelHTTP
# from channel_input_imgur import ChannelImgur
# from channel_input_linkedin import ChannelLinkedIn
# from channel_input_bitcoin import ChannelBitcoin
# from channel_input_smtp import ChannelSMTP
# from channel_output_email import EmailOutputChannel
# from channel_output_twilio import TwilioOutputChannel
# from channel_output_webhook import WebhookOutputChannel
from switchboard import Switchboard

# from queries import update_tor_exit_nodes_loop

log.err('Canarydrops switchboard started')

application = service.Application("Canarydrops Switchboard")

# f = logfile.LogFile.fromFullPath(settings.LOG_FILE, rotateLength=settings.SWITCHBOARD_LOG_SIZE,
#                                  maxRotatedFiles=settings.SWITCHBOARD_LOG_COUNT)
f = logfile.LogFile.fromFullPath('/tmp/twistedLogTest', rotateLength=500000000,
                                 maxRotatedFiles=20)
application.setComponent(ILogObserver, textFileLogObserver(f))
application.setComponent(ILogObserver, errorsToSlackLogObserver)
# application.setComponent(ILogObserver, errorsToSlackLogObserver())

switchboard = Switchboard()

# email_output_channel  = EmailOutputChannel(switchboard=switchboard)
# twilio_output_channel = TwilioOutputChannel(switchboard=switchboard)
# webhook_output_channel = WebhookOutputChannel(switchboard=switchboard)

dns_service = service.MultiService()

# factory = DNSServerFactory(
#     clients=[ChannelDNS(listen_domain=settings.LISTEN_DOMAIN,
#                         switchboard=switchboard)]
# )
# udp_factory = dns.DNSDatagramProtocol(factory)
# internet.TCPServer(settings.CHANNEL_DNS_PORT, factory)\
#             .setServiceParent(dns_service)
# internet.UDPServer(settings.CHANNEL_DNS_PORT, udp_factory)\
#             .setServiceParent(dns_service)
dns_service.setServiceParent(application)

canarytokens_httpd = ChannelHTTP(port=settings.CHANNEL_HTTP_PORT,
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
# loop_http = internet.task.LoopingCall(update_tor_exit_nodes_loop)
# loop_http.start(1800)

