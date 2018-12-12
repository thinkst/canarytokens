"""
Output channel that sends to webhooks.
"""
import settings
import pprint
import json

from twisted.python import log
import requests
import simplejson

from channel import OutputChannel
from constants import OUTPUT_CHANNEL_WEBHOOK

class WebhookOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_WEBHOOK


    def do_send_alert(self, input_channel=None, canarydrop=None, **kwargs):

        slack = "https://hooks.slack.com"

        if (slack in canarydrop['alert_webhook_url']):
            try:
                payload = input_channel.format_webhook_canaryalert(
                                              canarydrop=canarydrop,
                                              **kwargs)
                self.generic_webhook_send(json.dumps(payload), canarydrop)
            except Exception as e:
                log.err(e)
        else:
            try:
                payload = input_channel.format_webhook_canaryalert(
                                              canarydrop=canarydrop,
                                              **kwargs)
                self.generic_webhook_send(simplejson.dumps(payload), canarydrop)
            except Exception as e:
                log.err(e)

    def generic_webhook_send(self, payload=None, canarydrop=None):

        slack = "https://hooks.slack.com"

        if (slack in canarydrop['alert_webhook_url']):
            try:
                response = requests.post(canarydrop['alert_webhook_url'], data=payload, headers={'content-type': 'application/json'})
                response.raise_for_status()
                log.msg('Webhook sent to {url}'.format(url=canarydrop['alert_webhook_url']))
                return None
            except requests.exceptions.RequestException as e:
                log.err("Failed sending request to webhook {url} with error {error}".format(url=canarydrop['alert_webhook_url'],error=e))
                return e
        else:
            try:
                response = requests.post(canarydrop['alert_webhook_url'], payload, headers={'content-type': 'application/json'})
                response.raise_for_status()
                log.msg('Webhook sent to {url}'.format(url=canarydrop['alert_webhook_url']))
                return None
            except requests.exceptions.RequestException as e:
                log.err("Failed sending request to webhook {url} with error {error}".format(url=canarydrop['alert_webhook_url'],error=e))
                return e
