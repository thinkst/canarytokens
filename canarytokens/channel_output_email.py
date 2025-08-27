"""
Output channel that sends emails. Relies on Sendgrid to actually send mails.
"""
from pathlib import Path
from textwrap import dedent
import textwrap
from typing import Optional, Union
import enum
import uuid

import minify_html
import requests
import sendgrid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    AnyTokenExposedHit,
    Memo,
    TokenExposedHit,
    READABLE_TOKEN_TYPE_NAMES,
    TokenAlertDetails,
    TokenExposedDetails,
    TOKEN_TYPES_WITH_ARTICLE_AN,
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

    # NOT_SENT = "not_sent"
    SENT = "sent"
    ERROR = "error"
    # DELIVERED = "delivered"
    IGNORED = "ignored"


class EmailTemplates(str, enum.Enum):
    NOTIFICATION_TOKEN_EXPOSED = (
        "emails/_generated_dont_edit_notification_token_exposed.html"
    )
    NOTIFICATION = "emails/_generated_dont_edit_notification.html"


class EmailResponse(object):
    def __init__(
        self,
        status: EmailResponseStatuses,
        canarydrop: Canarydrop,
        message_id: str,
        alert_details: Union[TokenAlertDetails, TokenExposedDetails],
        max_alert_failures: int,
    ):
        self.status = status
        self.canarydrop = canarydrop
        self.message_id = message_id
        self.alert_details = alert_details
        self.max_alert_failures = max_alert_failures

    def handle(self):
        method_name = f"handle_{self.status.value}"
        m = getattr(self, method_name)
        return m()

    def handle_ignored(self):
        log.debug(
            f"Ignored email provider error received. Disabling {self.canarydrop.canarytoken.value()}."
        )
        self.canarydrop.disable_alert_email()

    def handle_sent(self):
        time = (
            self.alert_details.time
            if isinstance(self.alert_details, TokenAlertDetails)
            else self.alert_details.exposed_time
        )
        queries.remove_mail_from_to_send_status(
            token=self.alert_details.token,
            time=time,
        )
        queries.put_mail_on_sent_queue(
            mail_key=self.message_id,
            details=self.alert_details,
        )
        self.canarydrop.clear_alert_failures()

    def handle_error(self):
        self.canarydrop.record_alert_failure()
        if self.canarydrop.alert_failure_count > self.max_alert_failures:
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
    email_response = EmailResponseStatuses.ERROR
    message_id = ""
    try:
        response = sendgrid_client.send(message=mail)
        if response.status_code not in [202, 200]:
            email_response = EmailResponseStatuses.ERROR
            log.error(
                f"status code: {response.status_code}. Body: {response.body}",
            )
    except HTTPError as e:
        email_response = EmailResponseStatuses.ERROR
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
    email_response = EmailResponseStatuses.ERROR
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


def smtp_send(
    *,
    email_address: EmailStr,
    email_content_html: str,
    email_content_text: str,
    email_subject: str,
    from_email: EmailStr,
    from_display: str,
    smtp_password: str,
    smtp_username: str,
    smtp_server: str,
    smtp_port: str,
) -> tuple[EmailResponseStatuses, str]:
    email_response = EmailResponseStatuses.ERROR
    message_id = uuid.uuid4().hex
    try:
        fromaddr = from_email
        toaddr = email_address
        smtpmsg = MIMEMultipart("alternative")
        smtpmsg["From"] = from_display
        smtpmsg["To"] = email_address
        smtpmsg["Subject"] = email_subject
        part1 = MIMEText(email_content_text, "plain")
        part2 = MIMEText(email_content_html, "html")
        smtpmsg.attach(part1)
        smtpmsg.attach(part2)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_username is not None and smtp_password is not None:
                server.starttls()
                server.login(smtp_username, smtp_password)
            server.sendmail(fromaddr, toaddr, smtpmsg.as_string())
    except smtplib.SMTPException as e:
        log.error("A smtp error occurred: %s - %s" % (e.__class__, e))
        email_response = EmailResponseStatuses.ERROR
    else:
        email_response = EmailResponseStatuses.SENT
    return email_response, message_id


def send_email(
    *,
    switchboard_settings: SwitchboardSettings,
    email_recipient: EmailStr,
    email_subject: str,
    email_content_html: str,
    email_content_text: str,
    from_email: EmailStr,
    from_display: str,
) -> tuple[Optional[EmailResponseStatuses], Optional[str]]:
    if switchboard_settings.MAILGUN_API_KEY:
        email_response_status, message_id = mailgun_send(
            email_address=email_recipient,
            email_subject=email_subject,
            email_content_html=email_content_html,
            email_content_text=email_content_text,
            from_email=EmailStr(from_email),
            from_display=from_display,
            api_key=switchboard_settings.MAILGUN_API_KEY,
            base_url=switchboard_settings.MAILGUN_BASE_URL,
            mailgun_domain=switchboard_settings.MAILGUN_DOMAIN_NAME,
        )
    elif switchboard_settings.SENDGRID_API_KEY:
        email_response_status, message_id = sendgrid_send(
            api_key=switchboard_settings.SENDGRID_API_KEY,
            email_address=email_recipient,
            email_content_html=email_content_html,
            from_email=EmailStr(from_email),
            email_subject=email_subject,
            from_display=from_display,
            sandbox_mode=False,
        )
    elif switchboard_settings.SMTP_SERVER:
        email_response_status, message_id = smtp_send(
            email_address=email_recipient,
            email_content_html=email_content_html,
            email_content_text=email_content_text,
            email_subject=email_subject,
            from_email=EmailStr(from_email),
            from_display=from_display,
            smtp_password=switchboard_settings.SMTP_PASSWORD,
            smtp_username=switchboard_settings.SMTP_USERNAME,
            smtp_server=switchboard_settings.SMTP_SERVER,
            smtp_port=switchboard_settings.SMTP_PORT,
        )
    else:
        log.error("No email settings found")
        email_response_status, message_id = None, None
    return email_response_status, message_id


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
    def format_token_exposed_html(
        details: TokenExposedDetails,
        template_path: Path,
    ):
        """Returns a string containing an incident report in HTML,
        suitable for emailing"""
        readable_type = READABLE_TOKEN_TYPE_NAMES[details.token_type]
        BasicDetails = details.dict()
        BasicDetails["readable_type"] = readable_type
        BasicDetails["token_type"] = details.token_type.value
        BasicDetails["memo"] = details.memo
        BasicDetails["key_id"] = details.key_id
        BasicDetails["time_ymd"] = details.time_ymd
        BasicDetails["time_hm"] = details.time_hm

        rendered_html = Template(template_path.read_text()).render(
            BasicDetails=BasicDetails,
            ManageLink=details.manage_url,
            HistoryLink=details.history_url,
        )
        return minify_html.minify(rendered_html)

    @staticmethod
    def format_report_html(
        details: TokenAlertDetails,
        template_path: Path,
    ):
        """Returns a string containing an incident report in HTML,
        suitable for emailing"""

        # Use the Flask app context to render the emails
        # (this generates the urls + schemes correctly)
        readable_type = READABLE_TOKEN_TYPE_NAMES[details.token_type]
        BasicDetails = details.dict()
        BasicDetails["readable_type"] = readable_type
        BasicDetails["token_type"] = details.token_type.value

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

        if "useragent" in BasicDetails and not BasicDetails["useragent"]:
            BasicDetails.pop("useragent")
        if "src_ip" in BasicDetails and not BasicDetails["src_ip"]:
            BasicDetails.pop("src_ip")
        if details.token_type == TokenTypes.PWA and "location" in BasicDetails:
            BasicDetails["pwa_location"] = BasicDetails.pop("location")
            latitude = BasicDetails["pwa_location"]["coords"].get("latitude")
            longitude = BasicDetails["pwa_location"]["coords"].get("longitude")
            if latitude and longitude:
                BasicDetails["pwa_location"][
                    "google_maps_link"
                ] = f"https://google.com/maps?q={latitude},{longitude}"
                BasicDetails["pwa_location"][
                    "apple_maps_link"
                ] = f"https://maps.apple.com/?q={latitude},{longitude}"
        rendered_html = Template(template_path.open().read()).render(
            Title=EmailOutputChannel.DESCRIPTION,
            Intro=EmailOutputChannel.format_report_intro(details),
            BasicDetails=BasicDetails,
            ManageLink=details.manage_url,
            HistoryLink=details.history_url,
        )
        return minify_html.minify(rendered_html)

    @staticmethod
    def format_report_text(details: TokenAlertDetails):
        """Returns a string containing an incident report in text,
        suitable for emailing"""

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
    def format_token_exposed_text(details: TokenExposedDetails):
        """Returns a string containing an incident report in text,
        suitable for emailing"""
        body = textwrap.dedent(
            f"""
            One of your Canarytokens was exposed on the internet.
            Location: {details.public_location or "unknown"}
            Time    : {details.exposed_time}
            Memo    : {details.memo}
            Manage your settings for this Canarydrop:
            {details.manage_url}
            """
        ).strip()
        return body

    @staticmethod
    def format_token_exposed_intro(details: TokenExposedDetails):
        article = "An" if details.token_type in TOKEN_TYPES_WITH_ARTICLE_AN else "A"
        readable_type = READABLE_TOKEN_TYPE_NAMES[details.token_type]
        intro = (
            f"{article} {readable_type} Canarytoken has been exposed on the internet."
        )
        return intro

    @staticmethod
    def format_report_intro(details: TokenAlertDetails):
        details.channel
        details.token_type
        article = "An" if details.token_type in TOKEN_TYPES_WITH_ARTICLE_AN else "A"
        readable_type = READABLE_TOKEN_TYPE_NAMES[details.token_type]
        if details.src_ip:
            intro = f"{article} {readable_type} Canarytoken has been triggered by the Source IP {details.src_ip}"
        else:
            intro = f"{article} {readable_type} Canarytoken has been triggered."

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

        if (
            (details.token_type == TokenTypes.AWS_KEYS)
            and ("aws_key_log_data" in details.additional_data)
            and ("safety_net" in details.additional_data["aws_key_log_data"])
            and (details.additional_data["aws_key_log_data"]["safety_net"])
        ):
            intro = dedent(
                f"""{intro}
                    This AWS activity was caught using our safetynet feature so it may contain limited information.
                    """
            )

        return intro

    def do_send_alert(
        self,
        input_channel: InputChannel,
        canarydrop: Canarydrop,
        token_hit: Union[AnyTokenHit, AnyTokenExposedHit],
    ):
        if isinstance(token_hit, TokenExposedHit):
            details = TokenExposedDetails(
                token_type=token_hit.token_type,
                token=canarydrop.canarytoken.value(),
                key_id=canarydrop.aws_access_key_id,
                memo=Memo(canarydrop.memo),
                public_location=token_hit.public_location,
                exposed_time=token_hit.time_of_hit,
                manage_url=canarydrop.build_manage_url(
                    self.switchboard_scheme, self.hostname
                ),
                public_domain=self.hostname,
            )
        else:
            details = input_channel.gather_alert_details(
                canarydrop=canarydrop,
                host=self.switchboard_settings.PUBLIC_DOMAIN,
                protocol=self.switchboard_scheme,
            )

        queries.add_mail_to_send_status(
            recipient=canarydrop.alert_email_recipient,
            details=details,
        )

        if isinstance(details, TokenExposedDetails):
            email_content_html = EmailOutputChannel.format_token_exposed_html(
                details,
                Path(
                    self.switchboard_settings.TEMPLATES_PATH,
                    f"{EmailTemplates.NOTIFICATION_TOKEN_EXPOSED}",
                ),
            )
            email_content_text = EmailOutputChannel.format_token_exposed_text(details)
            email_subject = "Canarytoken Exposed"
        else:
            email_content_html = EmailOutputChannel.format_report_html(
                details,
                Path(
                    self.switchboard_settings.TEMPLATES_PATH,
                    f"{EmailTemplates.NOTIFICATION}",
                ),
            )
            email_content_text = EmailOutputChannel.format_report_text(details)
            email_subject = self.email_subject

        email_response_status, message_id = send_email(
            switchboard_settings=self.switchboard_settings,
            email_recipient=canarydrop.alert_email_recipient,
            email_subject=email_subject,
            email_content_html=email_content_html,
            email_content_text=email_content_text,
            from_email=EmailStr(self.from_email),
            from_display=self.from_display,
        )

        self.handle_email_response(
            EmailResponse(
                status=email_response_status,
                canarydrop=canarydrop,
                message_id=message_id,
                alert_details=details,
                max_alert_failures=self.switchboard_settings.MAX_ALERT_FAILURES,
            )
        )
        return details

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
