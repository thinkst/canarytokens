"""
Output channel that sends SMSs. Relies on Twilio to actually send SMSs.
"""
import settings
import pprint

from twisted.python import log
from twilio.rest import TwilioRestClient

from channel import OutputChannel
from constants import OUTPUT_CHANNEL_TWILIO_SMS
import settings

class TwilioOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_TWILIO_SMS


    def do_send_alert(self, input_channel=None, canarydrop=None, **kwargs):
        try:
            msg = input_channel.format_canaryalert(
                                          params={'body_length':140},
                                          canarydrop=canarydrop,
                                          **kwargs)

            client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            if len(canarydrop['alert_sms_recipient']) == 0:
                raise Exception('No SMS recipient for token: {token}'
                                .format(token=canarydrop['canarytoken']))

            if settings.DEBUG:
                pprint.pprint(msg)
            else:
                client.messages.create(
                    to=canarydrop['alert_sms_recipient'],
                    from_=settings.TWILIO_FROM_NUMBER,
                    body=msg['body']
                )
            log.msg('Sent SMS alert to {recipient} for token {token}'
                .format(recipient=canarydrop['alert_sms_recipient'],
                        token=canarydrop.canarytoken.value()))
        except Exception as e:
            log.err('Twilio send failed: {error}'.format(error=e))
