from httpx import HTTPError
import requests
from zope.interface import implementer
from twisted.logger import ILogObserver
from twisted.logger import LogLevel
import os

from twisted.logger import eventAsJSON, Logger

log = Logger()


# The below value comes up whenever a mailgun API requested is attempted
# And the intended recipient of the mail is an incorrectly entered/obviously wrong
# email address. eg `asd@x.xa`
text_for_failed_email_address_entered = "A mailgun error occurred: <class 'requests.exceptions.HTTPError'> - 400 Client Error: BAD REQUEST for url: https://api.mailgun.net/v3/canarytokens.org/messages"


@implementer(ILogObserver)
class errorsToWebhookLogObserver(object):
    """
    Log observer that sends errors out to a Slack endpoint.
    """

    def __init__(self, formatEvent):
        """
        @param formatEvent: A callable that formats an event.
        @type formatEvent: L{callable} that takes an C{event} argument and
            returns a formatted event as L{unicode}.
        """
        self.formatEvent = formatEvent

    def __call__(self, event):
        """
        Check if log_level Error or higher, if so post to webhook

        @param event: An event.
        @type event: L{dict}
        """
        if (
            event["log_level"] == LogLevel.error
            or event["log_level"] == LogLevel.critical
        ):
            if event["log_namespace"] == "log_legacy":
                # A log from the legacy logger has been called, therefore use a different key to get the log message
                postdata = {"text": event["log_text"]}
            else:
                postdata = {"text": event["log_format"]}
            if (
                postdata["text"] == "Unhandled error in Deferred:"
                or postdata["text"] == text_for_failed_email_address_entered
            ):
                # filters out non useful spam of messages seen before with these exact contents
                return
            url = os.getenv("ERROR_LOG_WEBHOOK").encode()
            headers = {b"Content-Type": b"application/json"}
            resp = requests.post(url=url, headers=headers, json=postdata)
            try:
                resp.raise_for_status()
            except HTTPError:
                log.warn("Failed to post to webhook")


def webhookLogObserver(recordSeparator="\x1e"):
    """
    Create a L{errorsToWebhookLogObserver} that emits error and critical
    loglines' text to a specified webhook URL by doing a HTTP POST.

    @param recordSeparator: The record separator to use.
    @type recordSeparator: L{unicode}

    @return: A log observer that POST critical and Error logs to a webhook.
    @rtype: L{errorsToWebhookLogObserver}

    """
    return errorsToWebhookLogObserver(
        lambda event: "{0}{1}\n".format(recordSeparator, eventAsJSON(event))
    )
