"""
Output channel that sends emails. Relies on Mandrill to actually send mails.
"""
import settings
import pprint

from twisted.python import log
import mandrill
import requests

from channel import OutputChannel
from constants import OUTPUT_CHANNEL_EMAIL

class EmailOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_EMAIL


    def do_send_alert(self, input_channel=None, canarydrop=None, **kwargs):
        msg = input_channel.format_canaryalert(
                                      params={'subject_required':True,
                                              'from_display_required':True,
                                              'from_address_required':True},
                                      canarydrop=canarydrop,
                                      **kwargs)
        if settings.MAILGUN_DOMAIN_NAME and settings.MAILGUN_API_KEY:
            mailgun_send(msg=msg,canarydrop=canarydrop)
        elif settings.MANDRILL_API_KEY:
            mandrill_send(msg=msg,canarydrop=canarydrop)
        else:
            log.err("No email settings found")

    def mailgun_send(self, msg=None, canarydrop=None):
        try:
            url = 'https://api.mailgun.net/v3/{}/messages'.format(settings.MAILGUN_DOMAIN_NAME)
            auth = ('api', settings.MAILGUN_API_KEY)
            data = {
                'from': '{name} <{address}>'.format(name=msg['from_display'],address=msg['from_address']),
                'to': canarydrop['alert_email_recipient'],
                'subject': msg['subject'],
                'text':  msg['body']
            }

            if settings.DEBUG:
                pprint.pprint(data)
            else:
                result = requests.post(url, auth=auth, data=data)
                #Raise an error if the returned status is 4xx or 5xx
                result.raise_for_status()

            log.msg('Sent alert to {recipient} for token {token}'\
                        .format(recipient=canarydrop['alert_email_recipient'],
                                token=canarydrop.canarytoken.value()))

        except requests.exceptions.HTTPError as e:
            log.err('A mailgun error occurred: %s - %s' % (e.__class__, e))

    def mandrill_send(self, msg=None, canarydrop=None):
        try:
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
