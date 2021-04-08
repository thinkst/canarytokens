from zope.interface import implementer, implements
from twisted.logger import ILogObserver
from twisted.logger import LogLevel
import json
import urllib

from twisted.logger import Logger
log = Logger()

from twisted.web.iweb import IBodyProducer
from twisted.internet import defer
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet import reactor
from twisted.internet import protocol
from zope.interface import implementer

from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer


@implementer(IBodyProducer)
class BytesProducer:
    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass



@implementer(ILogObserver)
class errorsToSlackLogObserver(object):
    """
    Log observer that sends errors out to a Slack endpoint.
    """
    def __init__(self, formatEvent):
        """
        @param outFile: A file-like object.  Ideally one should be passed which
            accepts L{unicode} data.  Otherwise, UTF-8 L{bytes} will be used.
        @type outFile: L{io.IOBase}

        @param formatEvent: A callable that formats an event.
        @type formatEvent: L{callable} that takes an C{event} argument and
            returns a formatted event as L{unicode}.
        """
        # import pudb; pudb.set_trace()
        self.formatEvent = formatEvent


    def __call__(self, event):
        """
        Check if log_level Error or higher, if so post to webhook

        @param event: An event.
        @type event: L{dict}
        """
        if event['log_level'] == LogLevel.error or event['log_level'] == LogLevel.critical:
            if event['log_namespace'] == "log_legacy":
                # A log from the legacy logger has been called, therefore use a different key to get the log message
                postdata = {'text':event['log_text']}
            else:
                postdata = {'text':event['log_format']}
            d = httpRequest(postdata)
        #     data = {'text':event['log_format']}
        #                 data=json.dumps(data))
        #

def httpRequest(postdata):
    # import pudb; pudb.set_trace()
    agent = Agent(reactor)
    headers={'Content-Type': ['application/x-www-form-urlencoded']}
    data_str = json.dumps(postdata)
    body = BytesProducer(data_str)
    # TODO burnt the below webhook straight after committing to GH
    d = agent.request("POST", url, Headers(headers), body)

    def handle_response(response):
        # import pudb; pudb.set_trace()
        if response.code == 200:
            d = defer.succeed('')
        else:
            log.warn('Failed to post to webhook')
            d = None
            # class SimpleReceiver(protocol.Protocol):
            #     def __init__(s, d):
            #         s.buf = ''; s.d = d
            #     def dataReceived(s, data):
            #         s.buf += data
            #     def connectionLost(s, reason):
            #         # TODO: test if reason is twisted.web.client.ResponseDone, if not, do an errback
            #         s.d.callback(s.buf)

            # d = defer.Deferred()
            # response.deliverBody(SimpleReceiver(d))
        return d

    d.addCallback(handle_response)
    return d

def webhookLogObserver(recordSeparator=u"\x1e"):
    """

    """
    return errorsToSlackLogObserver(
        lambda event: u"{0}{1}\n".format(recordSeparator, eventAsJSON(event))
    )

# def slack_handler():
#     SLACK_WEBHOOK = commonconfig.getVal('slack.exceptions_webhook', default="")
#     SLACK_CHANNEL = commonconfig.getVal('slack.exceptions_channel', default="")
#     SLACK_USERNAME = commonconfig.getVal('slack.exceptions_username', default="")

#     if not SLACK_WEBHOOK or not SLACK_CHANNEL or not SLACK_USERNAME :
#         raise SlackException("Slack config settings not present or not set.  No Slack exception reporting will take place.")

#     handler = SlackChannelHandler(SLACK_WEBHOOK, SLACK_CHANNEL, SLACK_USERNAME)

#     handler.setLevel(logging.ERROR)
#     hostname= commonconfig.getVal('console.domain')
#     formatter = logging.Formatter('{} [%(levelname)s - %(filename)s:%(lineno)d]: %(asctime)s  %(name)s: %(message)s'.format(hostname))
#     handler.setFormatter(formatter)
#     handler.addFilter(SlackFilter())
#     return handler

# class FileLogObserver:
#     """
#     Log observer that writes to a file-like object.

#     @type timeFormat: C{str} or C{NoneType}
#     @ivar timeFormat: If not C{None}, the format string passed to strftime().
#     """
#     timeFormat = None

#     def __init__(self, f):
#         self.write = f.write
#         self.flush = f.flush