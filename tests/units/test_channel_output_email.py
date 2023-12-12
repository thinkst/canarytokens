import datetime
from pathlib import Path
import uuid
from pydantic import EmailStr
import pytest
from unittest.mock import patch
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
)
from canarytokens.models import (
    DNSTokenHistory,
    DNSTokenHit,
    Memo,
    TokenAlertDetails,
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
    email_template = EmailOutputChannel.format_report_html(
        details, Path(f"{settings.TEMPLATES_PATH}/emails/notification.html")
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
            "referer": "https://someone.not.nice/stuff",
            "location": "https://fake.your/domain/stuff",
        },
    )
    email_template = EmailOutputChannel.format_report_html(
        details, Path(f"{settings.TEMPLATES_PATH}/emails/notification.html")
    )
    assert "https://some.link/manage/here" in email_template
    assert "https://some.link/history/here" in email_template
    assert "https://someone.not.nice/stuff" in email_template
    assert "https://fake.your/domain/stuff" in email_template


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
            "referer": "https://someone.not.nice/stuff/ref",
            "location": "https://fake.your/domain/stuff/loc",
        },
    )
    email_template = EmailOutputChannel.format_report_html(
        details, Path(f"{settings.TEMPLATES_PATH}/emails/notification.html")
    )
    assert "https://some.link/manage/here" in email_template
    assert "https://some.link/history/here" in email_template
    assert "https://someone.not.nice/stuff/ref" in email_template
    assert "https://fake.your/domain/stuff/loc" in email_template


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
    email_template = EmailOutputChannel.format_report_html(
        details, Path(f"{settings.TEMPLATES_PATH}/emails/notification.html")
    )
    assert "https://some.link/manage/here" in email_template
    assert "https://some.link/history/here" in email_template
    assert "SRV01" in email_template


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
    email_template = EmailOutputChannel.format_report_html(
        details, Path(f"{settings.TEMPLATES_PATH}/emails/notification.html")
    )
    assert "https://some.link/manage/here" in email_template
    assert "https://some.link/history/here" in email_template
    assert "SES" in email_template
    assert "Service Used" in email_template


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
    "email,expected_result_type",
    [
        (
            "http://notawebsiteIhopeorknowof.invalid",
            EmailResponseStatuses.ERROR,
        ),
        ("tokens-testing@thinkst.com", EmailResponseStatuses.SENT),
        ("testing@notawebsiteIhopeorknowof.invalid", EmailResponseStatuses.SENT),
    ],
)
def test_sendgrid_send(
    settings: SwitchboardSettings,
    email: str,
    expected_result_type: EmailResponseStatuses,
):
    if not settings.SENDGRID_API_KEY:
        pytest.skip("No SendGrid API key found; skipping...")
    details = _get_send_token_details()

    result, message_id = sendgrid_send(
        api_key=settings.SENDGRID_API_KEY,
        email_content_html=EmailOutputChannel.format_report_html(
            details, Path(f"{settings.TEMPLATES_PATH}/emails/notification.html")
        ),
        email_address=EmailStr(email),
        from_email=settings.ALERT_EMAIL_FROM_ADDRESS,
        email_subject=settings.ALERT_EMAIL_SUBJECT,
        from_display=settings.ALERT_EMAIL_FROM_DISPLAY,
        sandbox_mode=True,
    )
    assert result
    assert result is expected_result_type
    if result == EmailResponseStatuses.SENT:
        assert len(message_id) > 0


@pytest.mark.parametrize(
    "email,expected_result_type",
    [
        (
            "http://notawebsiteIhopeorknowof.invalid",
            EmailResponseStatuses.IGNORED,
        ),
        ("tokens-testing@thinkst.com", EmailResponseStatuses.SENT),
        ("testing@notawebsiteIhopeorknowof.invalid", EmailResponseStatuses.SENT),
    ],
)
def test_mailgun_send(
    settings: SwitchboardSettings,
    email: str,
    expected_result_type: EmailResponseStatuses,
):
    if not settings.MAILGUN_API_KEY:
        pytest.skip("No Mailgun API key found; skipping...")
    details = _get_send_token_details()
    result, message_id = mailgun_send(
        email_content_html=EmailOutputChannel.format_report_html(
            details, Path(f"{settings.TEMPLATES_PATH}/emails/notification.html")
        ),
        email_content_text=EmailOutputChannel.format_report_text(details),
        email_address=EmailStr(email),
        from_email=settings.ALERT_EMAIL_FROM_ADDRESS,
        email_subject=settings.ALERT_EMAIL_SUBJECT,
        from_display=settings.ALERT_EMAIL_FROM_DISPLAY,
        api_key=settings.MAILGUN_API_KEY,
        base_url=settings.MAILGUN_BASE_URL,
        mailgun_domain=settings.MAILGUN_DOMAIN_NAME,
    )
    assert result
    assert result is expected_result_type
    if result == EmailResponseStatuses.SENT:
        assert len(message_id) > 0


# @pytest.mark.parametrize(
#     "email,expected_result_type",
#     [
#         (
#             "http://notawebsiteIhopeorknowof.invalid",
#             EmailResponseStatuses.IGNORED,
#         ),
#         ("tokens-testing@thinkst.com", EmailResponseStatuses.SENT),
#         ("testing@notawebsiteIhopeorknowof.invalid", EmailResponseStatuses.SENT),
#     ],
# )
@patch("canarytokens.channel_output_email.smtplib.SMTP", autospec=True)
def test_smtp_send(
    mock_SMTP,
    settings: SwitchboardSettings,
    # email: str,
    # expected_result_type: EmailResponseStatuses,
):
    details = _get_send_token_details()
    result, message_id = smtp_send(
        email_content_html=EmailOutputChannel.format_report_html(
            details, Path(f"{settings.TEMPLATES_PATH}/emails/notification.html")
        ),
        email_content_text=EmailOutputChannel.format_report_text(details),
        email_address=EmailStr("tokens-testing@thinkst.com"),
        from_email=settings.ALERT_EMAIL_FROM_ADDRESS,
        email_subject=settings.ALERT_EMAIL_SUBJECT,
        from_display=settings.ALERT_EMAIL_FROM_DISPLAY,
        smtp_password="testpassword",
        smtp_port=1025,
        smtp_server="localhost",
        smtp_username="testuser",
    )
    # import pdb; pdb.set_trace()
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 1
    assert len(message_id) == len(uuid.uuid4().hex)
    # assert result
    # assert result is expected_result_type
    # if result == EmailResponseStatuses.SENT:
    #     assert len(message_id) > 0


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
                    time_of_hit=datetime.datetime.utcnow().timestamp(),
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


def test_bad_format_email(
    frontend_settings: FrontendSettings, settings: SwitchboardSettings, setup_db
):
    canarydrop = _do_send_alert(
        frontend_settings, settings, "http://testinganemailaddressurl.haha"
    )
    # Check canarydrop has been disabled
    assert (
        len(canarydrop.get_requested_output_channels()) == 0
    ), "A requested output channel is enabled still."
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
                    time_of_hit=datetime.datetime.utcnow().timestamp(),
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
