"""
Output channel that sends to webhooks.
"""
import settings
import pprint

from twisted.logger import Logger
log = Logger()
import requests
import simplejson

from channel import OutputChannel
from constants import OUTPUT_CHANNEL_WEBHOOK

class WebhookOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_WEBHOOK


    def do_send_alert(self, input_channel=None, canarydrop=None, **kwargs):

        slack = "https://hooks.slack.com"

        try:
            if (slack in canarydrop['alert_webhook_url']):
                payload = input_channel.format_slack_canaryalert(
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

        try:
            response = requests.post(canarydrop['alert_webhook_url'], payload, headers={'content-type': 'application/json'})
            response.raise_for_status()
            log.info('Webhook sent to {url}'.format(url=canarydrop['alert_webhook_url']))
            return None
        except requests.exceptions.RequestException as e:
            log.error("Failed sending request to webhook {url} with error {error}".format(url=canarydrop['alert_webhook_url'],error=e))
            return e
