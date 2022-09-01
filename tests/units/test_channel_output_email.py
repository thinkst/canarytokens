import datetime
from pathlib import Path

from pydantic import EmailStr
from twisted.logger import capturedLogs

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import InputChannel
from canarytokens.channel_output_email import EmailOutputChannel
from canarytokens.models import (
    DNSTokenHistory,
    DNSTokenHit,
    Memo,
    TokenAlertDetails,
    TokenTypes,
)
from canarytokens.settings import BackendSettings, Settings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken


def test_dns_rendered_html(settings: Settings):
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


def test_slow_redirect_rendered_html(settings: Settings):
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


def test_log4shell_rendered_html(settings: Settings):
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


def test_sendgrid_send(settings: Settings, backend_settings: BackendSettings):
    sb = Switchboard()
    details = TokenAlertDetails(
        channel="DNS",
        token=Canarytoken().value(),
        token_type=TokenTypes.DNS,
        src_ip="127.0.0.1",
        time=datetime.datetime.now(),
        memo="This is a test Memo",
        manage_url="https://some.link/manage/here",
        additional_data={},
    )

    email_output_channel = EmailOutputChannel(
        backend_settings=backend_settings,
        settings=settings,
        switchboard=sb,
    )

    success, message_id = email_output_channel.sendgrid_send(
        api_key=settings.SENDGRID_API_KEY,
        email_content=EmailOutputChannel.format_report_html(
            details, Path(f"{settings.TEMPLATES_PATH}/emails/notification.html")
        ),
        email_address=EmailStr("benjamin+token-tester@thinkst.com"),
        from_email=settings.ALERT_EMAIL_FROM_ADDRESS,
        email_subject=settings.ALERT_EMAIL_SUBJECT,
        from_email_display=settings.ALERT_EMAIL_FROM_DISPLAY,
        sandbox_mode=True,
    )
    assert success
    assert len(message_id) > 0


def test_do_send_alert(backend_settings: BackendSettings, settings: Settings, setup_db):

    email_channel = EmailOutputChannel(
        backend_settings=backend_settings, settings=settings, switchboard=Switchboard()
    )
    canarydrop = Canarydrop(
        canarytoken=Canarytoken(),
        type=TokenTypes.DNS,
        alert_email_enabled=True,
        alert_email_recipient=EmailStr("benjamin+test@thinkst.com"),
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
            backend_hostname="127.0.0.1",
            backend_scheme="http",
            name="DNS",
        ),
    )
    # Check that the mail is successfully added to the sent queue.
    mail_key, details = queries.pop_mail_off_sent_queue()
    assert details.memo == canarydrop.memo
    assert mail_key is not False


def test_do_send_alert_retries(
    backend_settings: BackendSettings, settings: Settings, setup_db
):
    """
    Test that email alert failures are retried and that the details and
    recipient are save to redis.
    """
    settings.__dict__["ALERT_EMAIL_FROM_ADDRESS"] = "illegal@address.com"
    # Ensure we not hitting the sandbox which accepts all.
    settings.__dict__["SENDGRID_SANDBOX_MODE"] = False
    email_channel = EmailOutputChannel(
        backend_settings=backend_settings, settings=settings, switchboard=Switchboard()
    )
    recipient = EmailStr("benjamin+test@thinkst.com")
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
                backend_hostname="127.0.0.1",
                backend_scheme="http",
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
