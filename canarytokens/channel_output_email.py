"""
Output channel that sends emails. Relies on Sendgrid to actually send mails.
"""
from pathlib import Path
from textwrap import dedent
import textwrap
from typing import Optional
import enum

import minify_html
import requests
import sendgrid
from jinja2 import Template
from pydantic import EmailStr, HttpUrl, SecretStr
from python_http_client.exceptions import HTTPError
from sendgrid.helpers.mail import Content, From, Mail, MailSettings, SandBoxMode, To
from twisted.logger import Logger

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import InputChannel, OutputChannel
from canarytokens.constants import OUTPUT_CHANNEL_EMAIL, MAILGUN_IGNORE_ERRORS
from canarytokens.models import (
    AnyTokenHit,
    readable_token_type_names,
    TokenAlertDetails,
    token_types_with_article_an,
    TokenTypes,
)
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.switchboard import Switchboard

# from canarytokens.utils import retry_on_returned_error

log = Logger()


# def should_retry_sendgrid(success: bool, message_id: str) -> bool:
#     if not success:
#         log.error("Failed to send mail via sendgrid.")
#     return not success


# def should_retry_mailgun(success: bool, message_id: str) -> bool:
#     if not success:
#         log.error("Failed to send mail via mailgun.")
#     return not success

# success                             -> sent
# badly formed such as http://bob.com -> ignored (error returned right away)
# bad domain                          -> sent
# unhandled error                     -> error (sent to slack to notify)
class EmailResponseStatuses(str, enum.Enum):
    """Enumerates all email responses"""

    NOT_SENT = "not_sent"
    SENT = "sent"
    ERROR = "error"
    # DELIVERED = "delivered"
    IGNORED = "ignored"


class EmailResponse(object):
    def _init__(
        self,
        status: EmailResponseStatuses,
        canarydrop: Canarydrop,
        message_id: str,
        alert_details: TokenAlertDetails,
    ):
        self.status = status
        self.canarydrop = canarydrop
        self.message_id = message_id
        self.alert_details = alert_details

    def handle(self):
        m = getattr(self, "handle_" + self.status.value)
        return m(self)

    def handle_ignored(self):
        log.debug(
            f"Ignored email provider error received. Disabling {self.canarydrop.canarytoken.value()}."
        )
        self.canarydrop.disable_alert_email()

    def handle_sent(self):
        queries.remove_mail_from_to_send_status(
            token=self.alert_details.token,
            time=self.alert_details.time,
        )
        queries.put_mail_on_sent_queue(
            mail_key=self.message_id,
            details=self.alert_details,
        )
        self.canarydrop.clear_alert_failures()

    def handle_error(self):
        self.canarydrop.record_alert_failure()
        if (
            self.canarydrop.alert_failure_count
            > self.switchboard.switchboard_settings.MAX_ALERT_FAILURES
        ):
            log.info(
                f"Email for token {self.canarydrop.canarytoken.value()} has returned too many errors, disabling it."
            )
            self.canarydrop.disable_alert_email()
            self.canarydrop.clear_alert_failures()
        else:
            log.error(f"Failed to send email for token {self.alert_details.token}.")

    def handle_not_sent(self):
        raise NotImplementedError()

    def handle_delivered(self):
        raise NotImplementedError()


# @retry_on_returned_error(retry_if=should_retry_sendgrid)
def sendgrid_send(
    *,
    api_key: SecretStr,
    email_address: EmailStr,
    email_content_html: str,
    from_email: EmailStr,
    from_display: EmailStr,
    email_subject: str,
    sandbox_mode: bool = False,
) -> tuple[EmailResponseStatuses, str]:
    sendgrid_client = sendgrid.SendGridAPIClient(
        api_key=api_key.get_secret_value().strip()
    )

    from_email = From(
        email=from_email,
        name=from_display,
        subject=email_subject,
    )
    to_emails = [
        To(
            email=email_address,
        )
    ]
    content = Content("text/html", email_content_html)
    mail = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=email_subject,
        html_content=content,
    )
    mail.mail_settings = MailSettings(sandbox_mode=SandBoxMode(enable=sandbox_mode))
    email_response = EmailResponseStatuses.NOT_SENT
    message_id = ""
    try:
        response = sendgrid_client.send(message=mail)
        if response.status_code not in [202, 200]:
            email_response = EmailResponseStatuses.ERROR
            log.error(
                f"status code: {response.status_code}. Body: {response.body}",
            )
    except HTTPError as e:
        log.error(
            f"A sendgrid error occurred. Status code: {e.status_code} {e.to_dict}",
        )
    else:
        email_response = EmailResponseStatuses.SENT
        message_id = response.headers.get("X-Message-Id")
    finally:
        return email_response, message_id


# @retry_on_returned_error(retry_if=should_retry_mailgun)
def mailgun_send(
    *,
    email_address: EmailStr,
    email_content_html: str,
    email_content_text: str,
    email_subject: str,
    from_email: EmailStr,
    from_display: str,
    api_key: SecretStr,
    base_url: HttpUrl,
    mailgun_domain: str,
) -> tuple[EmailResponseStatuses, str]:
    email_response = EmailResponseStatuses.NOT_SENT
    message_id = ""
    try:
        url = "{}/v3/{}/messages".format(base_url, mailgun_domain)
        auth = ("api", api_key.get_secret_value().strip())
        data = {
            "from": f"{from_display} <{from_email}>",
            "to": email_address,
            "subject": email_subject,
            "text": email_content_text,
            "html": email_content_html,
        }
        response = requests.post(url, auth=auth, data=data)
        # Raise an error if the returned status is 4xx or 5xx
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.json().get("message") in MAILGUN_IGNORE_ERRORS:
            log.debug(
                f"Ignored mailgun error message for {email_address}: '{response.json()['message']}'"
            )
            email_response = EmailResponseStatuses.IGNORED
        else:
            log.error(
                f"A mailgun error occurred sending a mail to {email_address}: {e.__class__} - {e}"
            )
            email_response = EmailResponseStatuses.ERROR
    else:
        email_response = EmailResponseStatuses.SENT
        message_id = response.json().get("id")
    finally:
        return email_response, message_id


class EmailOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_EMAIL

    DESCRIPTION = "Canarytoken triggered"
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S (UTC)"

    def __init__(
        self,
        switchboard: Switchboard,
        frontend_settings: FrontendSettings,
        switchboard_settings: SwitchboardSettings,
        name: Optional[str] = None,
    ):
        self.switchboard_settings = switchboard_settings
        self.from_email = switchboard_settings.ALERT_EMAIL_FROM_ADDRESS
        self.from_display = switchboard_settings.ALERT_EMAIL_FROM_DISPLAY
        self.email_subject = switchboard_settings.ALERT_EMAIL_SUBJECT
        super().__init__(
            switchboard,
            switchboard_scheme=switchboard_settings.SWITCHBOARD_SCHEME,
            frontend_domain=switchboard_settings.PUBLIC_DOMAIN,
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
        readable_type = readable_token_type_names[details.token_type]
        BasicDetails = details.dict()
        BasicDetails["readable_type"] = readable_type

        if (
            BasicDetails["additional_data"]
            and "src_data" in BasicDetails["additional_data"]
        ):
            BasicDetails["src_data"] = BasicDetails["additional_data"].pop("src_data")

        additional_data_keys = (
            list(BasicDetails["additional_data"].keys())
            if BasicDetails["additional_data"]
            else []
        )
        src_data_keys = (
            list(BasicDetails["src_data"].keys()) if BasicDetails["src_data"] else []
        )

        for field_name in additional_data_keys:
            if BasicDetails["additional_data"][field_name]:
                BasicDetails[field_name] = BasicDetails["additional_data"].pop(
                    field_name
                )
        BasicDetails.pop("additional_data")

        for field_name in src_data_keys:
            if BasicDetails["src_data"][field_name]:
                BasicDetails[field_name] = BasicDetails["src_data"].pop(field_name)
        BasicDetails.pop("src_data")

        rendered_html = Template(template_path.open().read()).render(
            Title=EmailOutputChannel.DESCRIPTION,
            Intro=EmailOutputChannel.format_report_intro(details),
            BasicDetails=BasicDetails,
            ManageLink=details.manage_url,
            HistoryLink=details.history_url,
        )
        return minify_html.minify(rendered_html)

    @staticmethod
    def format_report_text(details: TokenAlertDetails, body_length: int = 999999999):
        """Returns a string containing an incident report in text,
        suitable for emailing"""

        if body_length <= 140:
            body = """Canarydrop@{time} via {channel_name}: """.format(
                channel_name=details.channel, time=details.time
            )
            capacity = 140 - len(body)
            body += details.memo[:capacity]
        else:
            additional_data = "\n" + "\n".join(
                f"{k}: {v}" for k, v in details.additional_data.items()
            )
            body = textwrap.dedent(
                f"""
                One of your canarydrops was triggered.
                Channel: {details.channel}
                Time   : {details.time}
                Memo   : {details.memo}{additional_data}
                Manage your settings for this Canarydrop:
                {details.manage_url}
                """
            ).strip()
        return body

    @staticmethod
    def format_report_intro(details: TokenAlertDetails):
        details.channel
        details.token_type
        article = "An" if details.token_type in token_types_with_article_an else "A"
        readable_type = readable_token_type_names[details.token_type]
        intro = f"{article} {readable_type} Canarytoken has been triggered by the Source IP {details.src_ip}"

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
        alert_details = input_channel.gather_alert_details(
            canarydrop=canarydrop,
            host=self.switchboard_settings.PUBLIC_DOMAIN,
            protocol=self.switchboard_scheme,
        )
        #
        queries.add_mail_to_send_status(
            recipient=canarydrop.alert_email_recipient,
            details=alert_details,
        )
        if self.switchboard_settings.MAILGUN_API_KEY:
            email_response_status, message_id = mailgun_send(
                email_address=canarydrop.alert_email_recipient,
                email_subject=self.email_subject,
                email_content_html=EmailOutputChannel.format_report_html(
                    alert_details,
                    Path(
                        f"{self.switchboard_settings.TEMPLATES_PATH}/emails/notification.html"
                    ),
                ),
                email_content_text=EmailOutputChannel.format_report_text(alert_details),
                from_email=EmailStr(self.from_email),
                from_display=self.from_display,
                api_key=self.switchboard_settings.MAILGUN_API_KEY,
                base_url=self.switchboard_settings.MAILGUN_BASE_URL,
                mailgun_domain=self.switchboard_settings.MAILGUN_DOMAIN_NAME,
            )
        elif self.switchboard_settings.SENDGRID_API_KEY:
            email_response_status, message_id = sendgrid_send(
                api_key=self.switchboard_settings.SENDGRID_API_KEY,
                email_address=canarydrop.alert_email_recipient,
                email_content_html=EmailOutputChannel.format_report_html(
                    alert_details,
                    Path(
                        f"{self.switchboard_settings.TEMPLATES_PATH}/emails/notification.html"
                    ),
                ),
                from_email=EmailStr(self.from_email),
                email_subject=self.email_subject,
                from_display=self.from_display,
                sandbox_mode=False,
                # self.switchboard_settings.SENDGRID_SANDBOX_MODE,
            )
        elif self.switchboard_settings.SMTP_SERVER:
            raise NotImplementedError("SMTP_SERVER - not supported")
        else:
            log.error("No email settings found")

        self.handle_email_response(
            EmailResponse(email_response_status, canarydrop, message_id, alert_details)
        )
        return alert_details

    def handle_email_response(self, email_response: EmailResponse):
        return email_response.handle()

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
