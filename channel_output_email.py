"""
Output channel that sends emails. Relies on Mandrill to actually send mails.
"""
import settings
import pprint

from twisted.python import log
import mandrill

from channel import OutputChannel
from constants import OUTPUT_CHANNEL_EMAIL

class EmailOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_EMAIL


    def do_send_alert(self, input_channel=None, canarydrop=None, **kwargs):
        try:
            msg = input_channel.format_canaryalert(
                                          params={'subject_required':True, 
                                                  'from_display_required':True,
                                                  'from_address_required':True},
                                          canarydrop=canarydrop,
                                          **kwargs)

            mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
            message = {
             'auto_html': None,
             'auto_text': None,
             'from_email': msg['from_address'],
             'from_name': msg['from_display'],
             'text': msg['body'],
             'subject': msg['subject'],
             'to': [{'email': canarydrop['alert_email_recipient'],
                     'name': '',
                     'type': 'to'}],
            }
            if settings.DEBUG:
                pprint.pprint(message)
            else:
                result = mandrill_client.messages.send(message=message, 
                                                   async=False, 
                                                   ip_pool='Main Pool')
            log.msg('Sent alert to {recipient} for token {token}'\
                        .format(recipient=canarydrop['alert_email_recipient'],
                                token=canarydrop.canarytoken.value()))

        except mandrill.Error, e:
            # Mandrill errors are thrown as exceptions
            log.err('A mandrill error occurred: %s - %s' % (e.__class__, e))
            # A mandrill error occurred: <class 'mandrill.UnknownSubaccountError'> - No subaccount exists with the id 'customer-123'....

