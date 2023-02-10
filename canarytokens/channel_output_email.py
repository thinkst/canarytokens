"""
Output channel that sends emails. Relies on Sendgrid to actually send mails.
"""
from pathlib import Path
from textwrap import dedent
from typing import Optional

import minify_html
import sendgrid
from jinja2 import Template
from pydantic import EmailStr, SecretStr
from python_http_client.exceptions import HTTPError
from sendgrid.helpers.mail import Content, From, Mail, MailSettings, SandBoxMode, To
from twisted.logger import Logger

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import InputChannel, OutputChannel
from canarytokens.constants import OUTPUT_CHANNEL_EMAIL
from canarytokens.models import AnyTokenHit, TokenAlertDetails, TokenTypes
from canarytokens.settings import BackendSettings, Settings
from canarytokens.switchboard import Switchboard
from canarytokens.utils import retry_on_returned_error, token_type_as_readable

log = Logger()


class EmailOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_EMAIL

    DESCRIPTION = "Canarytoken triggered"
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S (UTC)"

    def __init__(
        self,
        switchboard: Switchboard,
        backend_settings: BackendSettings,
        settings: Settings,
        name: Optional[str] = None,
    ):
        self.settings = settings
        self.from_email = settings.ALERT_EMAIL_FROM_ADDRESS
        self.from_email_display = settings.ALERT_EMAIL_FROM_DISPLAY
        self.email_subject = settings.ALERT_EMAIL_SUBJECT
        super().__init__(
            switchboard,
            backend_scheme=backend_settings.BACKEND_SCHEME,
            backend_hostname=backend_settings.BACKEND_HOSTNAME,
            name=name,
        )

    @staticmethod
    def format_report_html(
        details: TokenAlertDetails,
        template_path: Path,
    ):
        """Returns a string containing an incident report in HTML,
        suitable for emailing"""

        # Use the Flask app context to render the emails
        # (this generates the urls + schemes correctly)
        BasicDetails = {
            "Description": details.memo,
            "Channel": details.channel,
            "Time": details.time,
            "Canarytoken": details.token,
            "SourceIP": details.src_ip,
            "TokenType": details.token_type,
        }
        for field_name, field_value in details.additional_data.items():
            if field_name in [
                "referer",
                "useragent",
                "location",
                "log4_shell_computer_name",
            ]:
                BasicDetails[field_name.capitalize()] = field_value

        if details.src_data and "generic_data" in details.src_data:
            BasicDetails["GenericData"] = details.src_data["generic_data"].decode()

        rendered_html = Template(template_path.open().read()).render(
            Title=EmailOutputChannel.DESCRIPTION,
            Intro=EmailOutputChannel.format_report_intro(details),
            BasicDetails=BasicDetails,
            ManageLink=details.manage_url,
            HistoryLink=details.history_url,
        )
        return minify_html.minify(rendered_html)

    @staticmethod
    def format_report_intro(details: TokenAlertDetails):
        details.channel
        details.token_type
        an_or_a = (
            "An"
            if details.token_type in [TokenTypes.ADOBE_PDF, TokenTypes.AWS_KEYS]
            else "A"
        )
        intro = f"{an_or_a} {token_type_as_readable(details.token_type)} Canarytoken has been triggered by the Source IP {details.src_ip}"

        if details.channel == "DNS":  # TODO: make channel an enum.
            intro = dedent(
                f"""{intro}
                    Please note that the source IP refers to a DNS server, rather than the host that triggered the token.
                    """
            )

        if (details.channel == "DNS") and (details.token_type == TokenTypes.MY_SQL):
            intro = dedent(
                f"""{intro}
                    Your MySQL token was tripped, but the attackers machine was unable to connect to the server directly. Instead, we can tell that it happened, and merely report on their DNS server. Source IP therefore refers to the DNS server used by the attacker.
                    """
            )

        return intro

    def do_send_alert(
        self,
        input_channel: InputChannel,
        canarydrop: Canarydrop,
        token_hit: AnyTokenHit,
    ):
        alert_details = input_channel.format_email_canaryalert(
            canarydrop=canarydrop,
            host=self.backend_hostname,
            protocol=self.backend_scheme,
        )
        #
        queries.add_mail_to_send_status(
            recipient=canarydrop.alert_email_recipient,
            details=alert_details,
        )
        if self.settings.SENDGRID_API_KEY:
            sent_successfully, message_id = EmailOutputChannel.sendgrid_send(
                api_key=self.settings.SENDGRID_API_KEY,
                email_address=canarydrop.alert_email_recipient,
                email_content=EmailOutputChannel.format_report_html(
                    alert_details,
                    Path(f"{self.settings.TEMPLATES_PATH}/emails/notification.html"),
                ),
                from_email=EmailStr(self.from_email),
                email_subject=self.email_subject,
                from_email_display=self.from_email_display,
                sandbox_mode=False,
                # self.settings.SENDGRID_SANDBOX_MODE,
            )
        elif self.settings.SMTP_SERVER:
            raise NotImplementedError("SMTP_SERVER - not supported")
        else:
            log.error("No email settings found")

        if sent_successfully:
            queries.remove_mail_from_to_send_status(
                token=alert_details.token,
                time=alert_details.time,
            )
            queries.put_mail_on_sent_queue(
                mail_key=message_id,
                details=alert_details,
            )
        else:
            log.error(f"Failed to send email for token {alert_details.token}.")
        return alert_details

    @staticmethod
    def should_retry_sendgrid(success: bool, message_id: str) -> bool:
        if not success:
            log.error("Failed to send mail via sendgrid.")
        return not success

    @staticmethod
    @retry_on_returned_error(retry_if=should_retry_sendgrid)
    def sendgrid_send(
        *,
        api_key: SecretStr,
        email_address: EmailStr,
        email_content: str,
        from_email: EmailStr,
        from_email_display: EmailStr,
        email_subject=str,
        sandbox_mode: bool = False,
    ) -> tuple[bool, str]:

        sendgrid_client = sendgrid.SendGridAPIClient(
            api_key=api_key.get_secret_value().strip()
        )

        from_email = From(
            email=from_email,
            name=from_email_display,
            subject=email_subject,
        )
        to_emails = [
            To(
                email=email_address,
            )
        ]
        content = Content("text/html", email_content)
        mail = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=email_subject,
            html_content=content,
        )
        mail.mail_settings = MailSettings(sandbox_mode=SandBoxMode(enable=sandbox_mode))
        sent_successfully = False
        message_id = ""
        try:
            response = sendgrid_client.send(message=mail)
            if response.status_code not in [202, 200]:
                sent_successfully = False
                log.error(
                    "status code: {status_code}. Body: {body}",
                    status_code=response.status_code,
                    body=response.body,
                )
        except HTTPError as e:
            log.error(
                "A sendgrid error occurred. Status code: {status_code} {data}",
                status_code=e.status_code,
                data=e.to_dict,
            )
        else:
            sent_successfully = True
            message_id = response.headers.get("X-Message-Id")
        finally:
            return sent_successfully, message_id

    @staticmethod
    def check_sendgrid_mail_status(api_key: str) -> bool:
        """
        WIP: account needs upgrade to hit this api.
        Checks a mail's status on send grid.
        REF: https://docs.sendgrid.com/api-reference/e-mail-activity/filter-messages-by-message-id
        Args:
            mail_key (str): message_id obtained from the sending of the mail.
            api_key (str): SendGrid api_key

        Returns:
            bool: returns True if mail was processed. False otherwise.
        """
        return
        # sg = sendgrid.SendGridAPIClient(api_key=api_key)
        # mail_key, alert_details = queries.pop_mail_off_sent_queue()
        # # Check using: resp = sg.client.messages._(mail_key).get()
        # if False:
        #     # delivery was not made.
        #     queries.put_mail_on_sent_queue(mail_key=mail_key, details=alert_details)
        # return mail_key is not None

    # def get_basic_details(self,):

    #     vars = { 'Description' : self.data['description'],
    #              'Channel'     : self.data['channel'],
    #              'Time'        : self.data['time'],
    #              'Canarytoken' : self.data['canarytoken']
    #             }

    #     if 'src_ip' in self.data:
    #         vars['src_ip'] = self.data['src_ip']
    #         vars['SourceIP'] = self.data['src_ip']

    #     if 'useragent' in self.data:
    #         vars['User-Agent'] = self.data['useragent']

    #     if 'tokentype' in self.data:
    #         vars['TokenType'] = self.data['tokentype']

    #     if 'referer' in self.data:
    #         vars['Referer'] = self.data['referer']

    #     if 'location' in self.data:
    #         try:
    #             vars['Location'] = self.data['location'].decode('utf-8')
    #         except Exception:
    #             vars['Location'] = self.data['location']

    #     if 'log4_shell_computer_name' in self.data:
    #         vars['Log4JComputerName'] = self.data['log4_shell_computer_name']

    #     return vars

    # def mailgun_send(self, msg=None, canarydrop=None):
    #     try:
    #         base_url = 'https://api.mailgun.net'
    #         if settings.MAILGUN_BASE_URL:
    #             base_url = settings.MAILGUN_BASE_URL
    #         url = '{}/v3/{}/messages'.format(base_url, settings.MAILGUN_DOMAIN_NAME)
    #         auth = ('api', settings.MAILGUN_API_KEY)
    #         data = {
    #             'from': '{name} <{address}>'.format(name=msg['from_display'],address=msg['from_address']),
    #             'to': canarydrop['alert_email_recipient'],
    #             'subject': msg['subject'],
    #             'text':  msg['body'],
    #             'html': self.format_report_html()
    #         }

    #         if settings.DEBUG:
    #             pprint.pprint(data)
    #         else:
    #             result = requests.post(url, auth=auth, data=data)
    #             #Raise an error if the returned status is 4xx or 5xx
    #             result.raise_for_status()

    #         log.info('Sent alert to {recipient} for token {token}'\
    #                     .format(recipient=canarydrop['alert_email_recipient'],
    #                             token=canarydrop.canarytoken.value()))

    #     except requests.exceptions.HTTPError as e:
    #         log.error('A mailgun error occurred: %s - %s' % (e.__class__, e))

    # def mandrill_send(self, msg=None, canarydrop=None):
    #     try:
    #         mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
    #         message = {
    #          'auto_html': None,
    #          'auto_text': None,
    #          'from_email': msg['from_address'],
    #          'from_name': msg['from_display'],
    #          'text': msg['body'],
    #          'html':self.format_report_html(),
    #          'subject': msg['subject'],
    #          'to': [{'email': canarydrop['alert_email_recipient'],
    #                  'name': '',
    #                  'type': 'to'}],
    #         }
    #         if settings.DEBUG:
    #             pprint.pprint(message)
    #         else:
    #             result = mandrill_client.messages.send(message=message,
    #                                                async=False,
    #                                                ip_pool='Main Pool')
    #         log.info('Sent alert to {recipient} for token {token}'\
    #                     .format(recipient=canarydrop['alert_email_recipient'],
    #                             token=canarydrop.canarytoken.value()))

    #     except mandrill.Error, e:
    #         # Mandrill errors are thrown as exceptions
    #         log.error('A mandrill error occurred: %s - %s' % (e.__class__, e))
    #         # A mandrill error occurred: <class 'mandrill.UnknownSubaccountError'> - No subaccount exists with the id 'customer-123'....

    # def smtp_send(self, msg=None, canarydrop=None):
    #     try:
    #         fromaddr = msg['from_address']
    #         toaddr = canarydrop['alert_email_recipient']

    #         smtpmsg = MIMEText(msg['body'])
    #         smtpmsg['From'] = fromaddr
    #         smtpmsg['To'] = toaddr
    #         smtpmsg['Subject'] = msg['subject']

    #         if settings.DEBUG:
    #             pprint.pprint(message)
    #         else:
    #             server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
    #             server.ehlo()
    #             server.starttls()
    #             server.ehlo()
    #             server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    #             text = smtpmsg.as_string()
    #             server.sendmail(fromaddr, toaddr, text)

    #         log.info('Sent alert to {recipient} for token {token}'\
    #             .format(recipient=canarydrop['alert_email_recipient'],
    #                 token=canarydrop.canarytoken.value()))
    #     except smtplib.SMTPException as e:
    #         log.error('A smtp error occurred: %s - %s' % (e.__class__, e))
