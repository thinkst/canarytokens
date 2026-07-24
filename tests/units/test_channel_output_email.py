import datetime
from pathlib import Path
import uuid
import pytest
import requests
from pydantic import EmailStr, HttpUrl, SecretStr
from python_http_client.exceptions import HTTPError
from unittest.mock import Mock
from unittest import mock
from twisted.logger import capturedLogs

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import InputChannel
from canarytokens.channel_output_email import (
    EmailOutputChannel,
    mailgun_send,
    sendgrid_send,
    smtp_send,
    EmailResponseStatuses,
    EmailTemplates,
)
from canarytokens.models import (
    DNSTokenHistory,
    DNSTokenHit,
    Memo,
    TokenAlertDetails,
    TokenExposedDetails,
    TokenTypes,
)
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken


def test_dns_rendered_html(settings: SwitchboardSettings):
    details = TokenAlertDetails(
        channel="DNS",
        token_type=TokenTypes.DNS,
        token=Canarytoken().value(),
        src_ip="127.0.0.1",
        time=datetime.datetime.now(),
        memo="This is a test Memo",
        manage_url="https://some.link/manage/here",
        additional_data={},
    )
    email_template = EmailOutputChannel.format_token_alert_mail(
        details,
        Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_HTML}"),
    )
    assert "https://some.link/manage/here" in email_template
    assert "https://some.link/history/here" in email_template


def test_slow_redirect_rendered_html(settings: SwitchboardSettings):
    details = TokenAlertDetails(
        channel="HTTP",
        token_type=TokenTypes.SLOW_REDIRECT,
        token=Canarytoken().value(),
        src_ip="127.0.0.1",
        time=datetime.datetime.now(),
        memo="This is a test Memo",
        manage_url="https://some.link/manage/here",
        additional_data={
            "useragent": "python 3.6",
            "location": "https://fake.your/domain/stuff",
        },
    )
    email_template = EmailOutputChannel.format_token_alert_mail(
        details,
        Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_HTML}"),
    )
    assert "https://some.link/manage/here" in email_template
    assert "https://some.link/history/here" in email_template


def test_cloned_site_rendered_html(settings: SwitchboardSettings):
    details = TokenAlertDetails(
        channel="HTTP",
        token_type=TokenTypes.CLONEDSITE,
        token=Canarytoken().value(),
        src_ip="127.0.0.1",
        time=datetime.datetime.now(),
        memo="This is a test Memo",
        manage_url="https://some.link/manage/here",
        additional_data={
            "useragent": "python 3.6",
            "location": "https://fake.your/domain/stuff/loc",
        },
    )
    email_template = EmailOutputChannel.format_token_alert_mail(
        details,
        Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_HTML}"),
    )
    assert "https://some.link/manage/here" in email_template
    assert "https://some.link/history/here" in email_template


def test_log4shell_rendered_html(settings: SwitchboardSettings):
    details = TokenAlertDetails(
        channel="DNS",
        token_type=TokenTypes.LOG4SHELL,
        token=Canarytoken().value(),
        src_ip="127.0.0.1",
        time=datetime.datetime.now(),
        memo="This is a test Memo",
        manage_url="https://some.link/manage/here",
        additional_data={
            "log4_shell_computer_name": "SRV01",
        },
    )
    email_template = EmailOutputChannel.format_token_alert_mail(
        details,
        Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_HTML}"),
    )
    assert "https://some.link/manage/here" in email_template
    assert "https://some.link/history/here" in email_template


def test_aws_keys_safetynet_rendered_html(settings: SwitchboardSettings):
    details = TokenAlertDetails(
        channel="HTTP",
        token_type=TokenTypes.AWS_KEYS,
        token=Canarytoken().value(),
        src_ip="127.0.0.1",
        time=datetime.datetime.now(),
        memo="This is a test Memo",
        manage_url="https://some.link/manage/here",
        additional_data={
            "aws_key_log_data": {"safety_net": ["True"], "service_used": ["ses"]}
        },
    )
    email_template = EmailOutputChannel.format_token_alert_mail(
        details,
        Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_HTML}"),
    )
    assert "https://some.link/manage/here" in email_template
    assert "https://some.link/history/here" in email_template


def test_aws_keys_event_name_rendered_in_notification_emails(
    settings: SwitchboardSettings,
):
    details = TokenAlertDetails(
        channel="HTTP",
        token_type=TokenTypes.AWS_KEYS,
        token=Canarytoken().value(),
        src_ip="127.0.0.1",
        time=datetime.datetime.now(),
        memo="This is a test Memo",
        manage_url="https://some.link/manage/here",
        additional_data={
            "aws_key_log_data": {"eventName": ["GetCallerIdentity"]},
        },
    )

    email_template_html = EmailOutputChannel.format_token_alert_mail(
        details,
        Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_HTML}"),
    )
    email_template_text = EmailOutputChannel.format_token_alert_mail(
        details,
        Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_TXT}"),
    )

    assert "Event Name" in email_template_html
    assert "GetCallerIdentity" in email_template_html
    assert "Event Name" in email_template_text
    assert "GetCallerIdentity" in email_template_text


def test_aws_key_exposed_rendered_html(settings: SwitchboardSettings):
    memo = "This is a test Memo"
    manage_url = "https://some.link/manage/here"
    public_location = "http://example.com/exposed/key"
    key_id = "ABCDEFG"

    details = TokenExposedDetails(
        token_type=TokenTypes.AWS_KEYS,
        token=Canarytoken().value(),
        memo=memo,
        manage_url=manage_url,
        key_id=key_id,
        public_location=public_location,
        exposed_time=datetime.datetime(2030, 12, 21, 12, 0, 0),
    )
    email_template = EmailOutputChannel.format_token_exposed_html(
        details,
        Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_TOKEN_EXPOSED}"),
    )
    assert memo in email_template
    assert manage_url in email_template
    assert public_location in email_template
    assert key_id in email_template
    assert "2030/12/21" in email_template
    assert "12:00" in email_template


def _get_send_token_details() -> TokenAlertDetails:
    return TokenAlertDetails(
        channel="DNS",
        token=Canarytoken().value(),
        token_type=TokenTypes.DNS,
        src_ip="127.0.0.1",
        time=datetime.datetime.now(),
        memo="This is a test Memo",
        manage_url="https://some.link/manage/here",
        additional_data={},
    )


@pytest.mark.parametrize(
    "status_code,expected_result_type",
    [
        (200, EmailResponseStatuses.SENT),
        (202, EmailResponseStatuses.SENT),
        (500, EmailResponseStatuses.ERROR),
    ],
)
@mock.patch(
    "canarytokens.channel_output_email.sendgrid.SendGridAPIClient", autospec=True
)
def test_sendgrid_send(
    mock_sendgrid_client,
    settings: SwitchboardSettings,
    status_code: int,
    expected_result_type: EmailResponseStatuses,
):
    mock_sendgrid_client.return_value.send.return_value = Mock(
        status_code=status_code,
        body="response body",
        headers={"X-Message-Id": "message-id"},
    )
    details = _get_send_token_details()

    result, message_id = sendgrid_send(
        api_key=SecretStr("test-sendgrid-api-key"),
        email_content_html=EmailOutputChannel.format_token_alert_mail(
            details,
            Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_HTML}"),
        ),
        email_address=EmailStr("tokens-testing@thinkst.com"),
        from_email=settings.ALERT_EMAIL_FROM_ADDRESS,
        email_subject=settings.ALERT_EMAIL_SUBJECT,
        from_display=settings.ALERT_EMAIL_FROM_DISPLAY,
        sandbox_mode=True,
    )
    assert result is expected_result_type
    if result == EmailResponseStatuses.SENT:
        assert message_id == "message-id"
    else:
        assert message_id == ""


@mock.patch(
    "canarytokens.channel_output_email.sendgrid.SendGridAPIClient", autospec=True
)
def test_sendgrid_send_http_error(mock_sendgrid_client):
    mock_sendgrid_client.return_value.send.side_effect = HTTPError(
        500,
        "Internal Server Error",
        b'{"errors": [{"message": "Internal Server Error"}]}',
        {},
    )

    result, message_id = sendgrid_send(
        api_key=SecretStr("test-sendgrid-api-key"),
        email_address=EmailStr("tokens-testing@thinkst.com"),
        email_content_html="test email content",
        from_email=EmailStr("sender@example.com"),
        from_display=EmailStr("sender@example.com"),
        email_subject="Test email",
    )

    assert result is EmailResponseStatuses.ERROR
    assert message_id == ""


@pytest.mark.parametrize(
    "status_code,response_body,expected_result_type,expected_message_id",
    [
        pytest.param(
            400,
            b'{"message": "to parameter is not a valid address. please check documentation"}',
            EmailResponseStatuses.IGNORED,
            "",
            id="ignorable email address",
        ),
        pytest.param(
            200,
            b'{"id": "message-id"}',
            EmailResponseStatuses.SENT,
            "message-id",
            id="successful send",
        ),
        pytest.param(
            500,
            b'{"message": "Internal Server Error"}',
            EmailResponseStatuses.ERROR,
            "",
            id="server error",
        ),
    ],
)
@mock.patch("canarytokens.channel_output_email.requests.post", autospec=True)
def test_mailgun_send(
    mock_post,
    status_code: int,
    response_body: bytes,
    expected_result_type: EmailResponseStatuses,
    expected_message_id: str,
):
    response = requests.Response()
    response.status_code = status_code
    response._content = response_body
    mock_post.return_value = response

    result, message_id = mailgun_send(
        email_address=EmailStr("tokens-testing@thinkst.com"),
        email_content_html="test email content",
        email_content_text="test email content",
        email_subject="Test email",
        from_email=EmailStr("sender@example.com"),
        from_display="Sender",
        api_key=SecretStr("test-mailgun-api-key"),
        base_url=HttpUrl("https://api.mailgun.test", scheme="https"),
        mailgun_domain="mailgun.test",
    )
    assert result is expected_result_type
    assert message_id == expected_message_id


# TODO: Write more comprehensive tests for SMTP. The difficulty here is that we don't have a consistent API to use
# because different SMTP servers may handle things differently. I figure as we break and enhance, we'll add tests too
@mock.patch("canarytokens.channel_output_email.smtplib.SMTP", autospec=True)
def test_smtp_send(
    mock_SMTP,
    settings: SwitchboardSettings,
):
    details = _get_send_token_details()
    result, message_id = smtp_send(
        email_content_html=EmailOutputChannel.format_token_alert_mail(
            details,
            Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_HTML}"),
        ),
        email_content_text=EmailOutputChannel.format_token_alert_mail(
            details, Path(settings.TEMPLATES_PATH, f"{EmailTemplates.NOTIFICATION_TXT}")
        ),
        email_address=EmailStr("tokens-testing@thinkst.com"),
        from_email=settings.ALERT_EMAIL_FROM_ADDRESS,
        email_subject=settings.ALERT_EMAIL_SUBJECT,
        from_display=settings.ALERT_EMAIL_FROM_DISPLAY,
        smtp_password="testpassword",
        smtp_port=1025,
        smtp_server="localhost",
        smtp_username="testuser",
    )
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 1
    assert len(message_id) == len(uuid.uuid4().hex)
    assert result == EmailResponseStatuses.SENT
    assert len(message_id) > 0


def _do_send_alert(
    frontend_settings: FrontendSettings,
    switchboard_settings: SwitchboardSettings,
    email: str,
) -> Canarydrop:
    if (
        not switchboard_settings.SENDGRID_API_KEY
        and not switchboard_settings.MAILGUN_API_KEY
    ):
        pytest.skip("No email provider API key found; skipping...")
    email_channel = EmailOutputChannel(
        frontend_settings=frontend_settings,
        switchboard_settings=switchboard_settings,
        switchboard=Switchboard(),
    )
    canarydrop = Canarydrop(
        canarytoken=Canarytoken(),
        type=TokenTypes.DNS,
        alert_email_enabled=True,
        alert_email_recipient=EmailStr(email),
        memo=Memo("Test email thanks for checking!"),
        triggered_details=DNSTokenHistory(
            hits=[
                DNSTokenHit(
                    time_of_hit=datetime.datetime.now(
                        datetime.timezone.utc
                    ).timestamp(),
                    src_ip="127.0.0.1",
                    input_channel="DNS",
                    is_tor_relay=False,
                )
            ]
        ),
    )
    email_channel.do_send_alert(
        canarydrop=canarydrop,
        token_hit=None,
        input_channel=InputChannel(
            switchboard=Switchboard(),
            switchboard_hostname="127.0.0.1",
            switchboard_scheme="http",
            name="DNS",
        ),
    )
    return canarydrop


def test_do_send_alert(
    frontend_settings: FrontendSettings, settings: SwitchboardSettings, setup_db
):
    canarydrop = _do_send_alert(
        frontend_settings, settings, "tokens-testing@thinkst.com"
    )
    # Check that the mail is successfully added to the sent queue.
    mail_key, details = queries.pop_mail_off_sent_queue()
    assert details.memo == canarydrop.memo
    assert mail_key is not False


@mock.patch(
    "canarytokens.channel_output_email.sendgrid.SendGridAPIClient", autospec=True
)
def test_sendgrid_http_error_does_not_mark_email_sent(
    mock_sendgrid_client,
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
    setup_db,
):
    mock_sendgrid_client.return_value.send.return_value = Mock(
        status_code=500,
        body="Internal Server Error",
        headers={},
    )
    sendgrid_settings = settings.copy(
        update={
            "MAILGUN_API_KEY": None,
            "SENDGRID_API_KEY": SecretStr("test-sendgrid-api-key"),
        }
    )

    canarydrop = _do_send_alert(
        frontend_settings,
        sendgrid_settings,
        "tokens-testing@thinkst.com",
    )

    mail_key, details = queries.pop_mail_off_sent_queue()
    assert mail_key is None
    assert details is None
    assert (
        len(queries.get_all_mails_in_send_status(token=canarydrop.canarytoken.value()))
        == 1
    )


@mock.patch("canarytokens.channel_output_email.requests.post", autospec=True)
def test_mailgun_http_error_does_not_mark_email_sent(
    mock_post,
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
    setup_db,
):
    response = requests.Response()
    response.status_code = 500
    response._content = b'{"message": "Internal Server Error"}'
    mock_post.return_value = response
    mailgun_settings = settings.copy(
        update={
            "MAILGUN_API_KEY": SecretStr("test-mailgun-api-key"),
            "SENDGRID_API_KEY": None,
        }
    )

    canarydrop = _do_send_alert(
        frontend_settings,
        mailgun_settings,
        "tokens-testing@thinkst.com",
    )

    mail_key, details = queries.pop_mail_off_sent_queue()
    assert mail_key is None
    assert details is None
    assert (
        len(queries.get_all_mails_in_send_status(token=canarydrop.canarytoken.value()))
        == 1
    )


def test_bad_format_email(
    frontend_settings: FrontendSettings, settings: SwitchboardSettings, setup_db
):
    canarydrop = _do_send_alert(
        frontend_settings, settings, "http://testinganemailaddressurl.haha"
    )
    # Check canarydrop has been disabled
    assert len(canarydrop.get_requested_output_channels()) == 0, (
        "A requested output channel is enabled still."
    )
    # Check that the mail is successfully added to the sent queue.
    queries_canarydrop = queries.get_canarydrop(canarydrop.canarytoken)
    assert queries_canarydrop.memo == canarydrop.memo
    assert queries_canarydrop.alert_email_enabled is False


def test_non_existent_email(
    frontend_settings: FrontendSettings, settings: SwitchboardSettings, setup_db
):
    """
    Tests whether an email that is syntactically valid, but doesn't exit should behave.

    Currently, we don't handled this case nicely because mailgun returns a 200 for valid emails
    that do not exist.
    """
    canarydrop = _do_send_alert(
        frontend_settings, settings, "testing@notanexistingdomainithinksurely.invalid"
    )
    # Check that the mail is successfully added to the sent queue.
    mail_key, details = queries.pop_mail_off_sent_queue()
    assert details.memo == canarydrop.memo
    assert mail_key is not False


@pytest.mark.skip(reason="disabled until retry is implemented async")
def test_do_send_alert_retries(
    frontend_settings: FrontendSettings, settings: SwitchboardSettings, setup_db
):
    """
    Test that email alert failures are retried and that the details and
    recipient are save to redis.
    """
    settings.__dict__["ALERT_EMAIL_FROM_ADDRESS"] = "illegal@address.com"
    # Ensure we not hitting the sandbox which accepts all.
    settings.__dict__["SENDGRID_SANDBOX_MODE"] = False
    # We can't trigger a failure this way with mailgun
    settings.__dict__["MAILGUN_API_KEY"] = None

    email_channel = EmailOutputChannel(
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
        switchboard=Switchboard(),
    )
    recipient = EmailStr("tokens-testing@thinkst.com")
    canarydrop = Canarydrop(
        canarytoken=Canarytoken(),
        type=TokenTypes.DNS,
        alert_email_enabled=True,
        alert_email_recipient=recipient,
        memo=Memo("Test email thanks for checking!"),
        triggered_details=DNSTokenHistory(
            hits=[
                DNSTokenHit(
                    time_of_hit=datetime.datetime.now(
                        datetime.timezone.utc
                    ).timestamp(),
                    src_ip="127.0.0.1",
                    input_channel="DNS",
                    is_tor_relay=False,
                )
            ]
        ),
    )
    with capturedLogs() as captured:
        alert_details = email_channel.do_send_alert(
            canarydrop=canarydrop,
            token_hit=None,
            input_channel=InputChannel(
                switchboard=Switchboard(),
                switchboard_hostname="127.0.0.1",
                switchboard_scheme="http",
                name="DNS",
            ),
        )
        # Check we failed to send
        assert any(
            ["Failed to send email for token" in log["log_format"] for log in captured]
        )
        # Check we tried 4 times
        assert (
            sum(
                [
                    "Failed to send mail via sendgrid." in log["log_format"]
                    for log in captured
                ]
            )
            == 4
        )

    items = queries.get_all_mails_in_send_status(token=canarydrop.canarytoken.value())
    assert len(items) == 1
    saved_recipient, saved_details = items[0]
    assert saved_recipient == recipient
    assert saved_details.json() == alert_details.json()
