# pragma: no cover
from twisted.logger import ILogObserver, Logger, LogLevel, eventAsText
from twisted.web.iweb import IBodyProducer
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet import defer, reactor
from twisted.internet.defer import succeed
from zope.interface import implementer

import os
import json

log = Logger()


# The below value comes up whenever a mailgun API requested is attempted
# And the intended recipient of the mail is an incorrectly entered/obviously wrong
# email address. eg `asd@x.xa`
text_for_failed_email_address_entered = "A mailgun error occurred: <class 'requests.exceptions.HTTPError'> - 400 Client Error: BAD REQUEST for url: https://api.mailgun.net/v3/canarytokens.org/messages"


@implementer(IBodyProducer)
class BytesProducer:
    def __init__(self, body):  # pragma: no cover
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):  # pragma: no cover
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):  # pragma: no cover
        pass

    def stopProducing(self):  # pragma: no cover
        pass


@implementer(ILogObserver)
class WebhookLogObserver:
    """
    Log observer that sends errors out to a Slack endpoint.
    """

    def __call__(self, event):  # pragma: no cover
        """
        Check if log_level Error or higher, if so post to webhook

        @param event: An event.
        @type event: L{dict}
        """
        if event["log_level"] in (LogLevel.error, LogLevel.critical):
            text = eventAsText(event, includeTimestamp=False)
            if (
                "Unhandled error in Deferred:" in text
                or text_for_failed_email_address_entered in text
            ):
                # filters out non useful spam of messages seen before with these exact contents
                return
            _ = httpRequest({"text": text})


def httpRequest(postdata):  # pragma: no cover
    agent = Agent(reactor)
    headers = {b"Content-Type": [b"application/json"]}
    data_str = json.dumps(postdata)
    body = BytesProducer(data_str.encode())
    url = os.getenv("ERROR_LOG_WEBHOOK").encode()
    d = agent.request(b"POST", url, Headers(headers), body)

    def handle_response(response):
        if response.code == 200:
            d = defer.succeed("")
        else:
            log.warn("Failed to post to webhook")
            d = None
        return d

    d.addCallback(handle_response)
    return d
