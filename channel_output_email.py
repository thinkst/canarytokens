"""
Output channel that sends emails. Relies on Mandrill to actually send mails.
"""
import settings
import pprint

from twisted.python import log
import mandrill
import requests
import sendgrid
from sendgrid.helpers.mail import *
from htmlmin import minify
from httpd_site import env
from channel import OutputChannel
from constants import OUTPUT_CHANNEL_EMAIL

class EmailOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_EMAIL

    DESCRIPTION = 'Canarytoken triggered'
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S (UTC)'

    def format_report_html(self,):
        """Returns a string containing an incident report in HTML,
           suitable for emailing"""

        # Use the Flask app context to render the emails
        # (this generates the urls + schemes correctly)

        rendered_html = env.get_template('emails/notification.html').render(
            Title=self.DESCRIPTION,
            Intro=self.format_report_intro(),
            BasicDetails=self.get_basic_details(),
            ManageLink=self.data['manage'],
            HistoryLink=self.data['history']
        )
        return minify(rendered_html)

    def format_report_intro(self,):
        if self.data['channel'] == 'HTTP':
            template = ("An {Type} Canarytoken has been triggered")
        else:
            template = ("A {Type} Canarytoken has been triggered")

        if 'src_ip' in self.data:
            template += " by the Source IP {src}.".format(src=self.data['src_ip'])

        if self.data['channel'] == 'DNS':
            template += "\n\nPlease note that the source IP refers to a DNS server," \
                        " rather than the host that triggered the token."

        return template.format(
            Type=self.data['channel'])


    def get_basic_details(self,):

        vars = { 'Description' : self.data['description'],
                 'Channel'     : self.data['channel'],
                 'Time'        : self.data['time'],
                 'Canarytoken' : self.data['canarytoken']
                }

        if 'src_ip' in self.data:
            vars['src_ip'] = self.data['src_ip']

        if 'useragent' in self.data:
            vars['User-Agent'] = self.data['useragent']

        if 'tokentype' in self.data:
            vars['TokenType'] = self.data['tokentype']

        if 'referer' in self.data:
            vars['Referer'] = self.data['referer']

        if 'location' in self.data:
            vars['Location'] = self.data['location']

        return vars

    def do_send_alert(self, input_channel=None, canarydrop=None, **kwargs):
        msg = input_channel.format_canaryalert(
                                      params={'subject_required':True,
                                              'from_display_required':True,
                                              'from_address_required':True},
                                      canarydrop=canarydrop,
                                      **kwargs)
        self.data = msg
        if 'type' in canarydrop._drop:
            self.data['tokentype']   = canarydrop._drop['type']

        self.data['canarytoken'] = canarydrop['canarytoken']
        self.data['description'] = canarydrop['memo']
        log.msg(settings.SENDGRID_API_KEY)
        log.msg(settings.MAILGUN_API_KEY)
        if settings.MAILGUN_DOMAIN_NAME and settings.MAILGUN_API_KEY:
            self.mailgun_send(msg=msg,canarydrop=canarydrop)
        elif settings.MANDRILL_API_KEY:
            self.mandrill_send(msg=msg,canarydrop=canarydrop)
        elif settings.SENDGRID_API_KEY:
            self.sendgrid_send(msg=msg,canarydrop=canarydrop)
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
                'text':  msg['body'],
                'html': self.format_report_html()
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
             'html':self.format_report_html(),
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

	def sendgrid_send(self, msg=None, canarydrop=None):
		try:
			sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
			from_email = Email(msg['from_address'])
			subject = msg['subject']
			to_email = Email(canarydrop['alert_email_recipient'])
			content = Content("text/plain", msg['body'])
			message = Mail(from_email, subject, to_email, content)
			
			if settings.DEBUG:
				pprint.pprint(message)
			else:
				result = sg.client.mail.send.post(request_body=message.get())
				
			log.msg('Sent alert to {recipient} for token {token}'\
                        .format(recipient=canarydrop['alert_email_recipient'],
                                token=canarydrop.canarytoken.value()))

        except requests.exceptions.HTTPError as e:
            log.err('A mailgun error occurred: %s - %s' % (e.__class__, e))
