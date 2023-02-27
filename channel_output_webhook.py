"""
Output channel that sends to webhooks.
"""
from zope.interface import implementer
from twisted.web.iweb import IBodyProducer
from twisted.internet.defer import succeed
from twisted.logger import Logger
log = Logger()
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
import simplejson

from channel import OutputChannel
from constants import OUTPUT_CHANNEL_WEBHOOK

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

class WebhookOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_WEBHOOK


    def do_send_alert(self, input_channel=None, canarydrop=None, **kwargs):
        slack_hook_base_url = "https://hooks.slack.com"
        googlechat_hook_base_url = "https://chat.googleapis.com/"

        try:
            if (slack_hook_base_url in canarydrop['alert_webhook_url']):
                payload = input_channel.format_slack_canaryalert(
                                            canarydrop=canarydrop,
                                            **kwargs)
            elif (googlechat_hook_base_url in canarydrop['alert_webhook_url']):
                payload = input_channel.format_googlechat_canaryalert(
                                            canarydrop=canarydrop,
                                            **kwargs)
            else:
                payload = input_channel.format_webhook_canaryalert(
                                            canarydrop=canarydrop,
                                            **kwargs)

            self.generic_webhook_send(simplejson.dumps(payload), canarydrop)
        except Exception as e:
            log.error(e)

    def generic_webhook_send(self, payload=None, canarydrop=None):

        def handle_response(response):
            if 200 <= response.code < 300:
                log.info('Request successfully sent to webhook {url}'.format(url=canarydrop['alert_webhook_url']))
            else:
                log.error("Webhook {url} responded with status code {status_code}. Payload: {payload}".format(
                    url=canarydrop['alert_webhook_url'],
                    status_code=response.code,
                    payload=payload))

        def handle_error(error):
            log.error("Failed to send request to webhook {url} with error {error}. Payload: {payload}".format(
                url=canarydrop['alert_webhook_url'],
                error=error,
                payload=payload))

        agent = Agent(reactor)
        body = BytesProducer(payload)
        d = agent.request("POST", canarydrop['alert_webhook_url'], Headers({'content-type': ['application/json']}), body)
        d.addCallback(handle_response)
        d.addErrback(handle_error)
