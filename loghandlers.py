from zope.interface import implementer
from twisted.logger import ILogObserver

@implementer(ILogObserver)
class errorsToSlackLogObserver(object):
    """
    Log observer that sends errors out to a Slack endpoint.
    """
    def __init__(self, outFile, formatEvent):
        """
        @param outFile: A file-like object.  Ideally one should be passed which
            accepts L{unicode} data.  Otherwise, UTF-8 L{bytes} will be used.
        @type outFile: L{io.IOBase}

        @param formatEvent: A callable that formats an event.
        @type formatEvent: L{callable} that takes an C{event} argument and
            returns a formatted event as L{unicode}.
        """
        import pudb; pudb.set_trace()
        # if ioType(outFile) is not unicode:
        #     self._encoding = "utf-8"
        # else:
        #     self._encoding = None

        # self._outFile = outFile
        # self.formatEvent = formatEvent


    def __call__(self, event):
        """
        Check if log_level Error or higher, if so post to Slack

        @param event: An event.
        @type event: L{dict}
        """
        import pudb; pudb.set_trace()
        # text = self.formatEvent(event)

        # if text is None:
        #     text = u""

        # if self._encoding is not None:
        #     text = text.encode(self._encoding)

        # if text:
        #     self._outFile.write(text)
        #     self._outFile.flush()

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