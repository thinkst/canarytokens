# pytest caplog
from twisted.logger import capturedLogs

from canarytokens.canarydrop import Canarydrop
from canarytokens.channel_dns import ChannelDNS
from canarytokens.channel_output_webhook import WebhookOutputChannel
from canarytokens.models import TokenTypes
from canarytokens.settings import Settings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken


def test_broken_webhook(setup_db, settings: Settings):
    switchboard = Switchboard()
    webhook_channel = WebhookOutputChannel(
        switchboard=switchboard,
        backend_scheme="https",
        backend_hostname="test.com",
    )
    cd = Canarydrop(
        type=TokenTypes.DNS,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url="https://broken.webhook.com/test",
        canarytoken=Canarytoken(),
        memo="memo",
        browser_scanner_enabled=False,
    )

    token_hit = Canarytoken.create_token_hit(
        token_type=TokenTypes.DNS,
        input_channel="not_valid",
        src_ip="127.0.0.1",
        hit_info={"some": "data"},
    )
    cd.add_canarydrop_hit(token_hit=token_hit)
    with capturedLogs() as captured:
        webhook_channel.send_alert(
            canarydrop=cd,
            token_hit=token_hit,
            input_channel=ChannelDNS(
                switchboard=switchboard,
                settings=settings,
                backend_hostname="test.com",
                backend_scheme="https",
                listen_domain=settings.LISTEN_DOMAIN,
            ),
        )
    assert any(
        ["Failed connecting to webhook" in log["log_format"] for log in captured]
    )


def test_webhook(setup_db, webhook_receiver, settings: Settings):
    switchboard = Switchboard()
    webhook_channel = WebhookOutputChannel(
        switchboard=switchboard,
        backend_scheme="https",
        backend_hostname="test.com",
    )
    cd = Canarydrop(
        type=TokenTypes.DNS,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=webhook_receiver,
        canarytoken=Canarytoken(),
        memo="memo",
        browser_scanner_enabled=False,
    )

    token_hit = Canarytoken.create_token_hit(
        token_type=TokenTypes.DNS,
        input_channel="not_valid",
        src_ip="127.0.0.1",
        hit_info={"some": "data"},
    )
    cd.add_canarydrop_hit(token_hit=token_hit)
    with capturedLogs() as captured:
        webhook_channel.send_alert(
            canarydrop=cd,
            token_hit=token_hit,
            input_channel=ChannelDNS(
                switchboard=switchboard,
                settings=settings,
                backend_hostname="test.com",
                backend_scheme="https",
                listen_domain=settings.LISTEN_DOMAIN,
            ),
        )
    assert any(["Successfully sent to " in log["log_format"] for log in captured])


def test_broken_2_webhook(setup_db, webhook_receiver, settings: Settings):
    switchboard = Switchboard()
    webhook_channel = WebhookOutputChannel(
        switchboard=switchboard,
        backend_scheme="https",
        backend_hostname="test.com",
    )
    cd = Canarydrop(
        type=TokenTypes.DNS,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=f"{webhook_receiver}/broken",
        canarytoken=Canarytoken(),
        memo="memo",
        browser_scanner_enabled=False,
    )

    token_hit = Canarytoken.create_token_hit(
        token_type=TokenTypes.DNS,
        input_channel="not_valid",
        src_ip="127.0.0.1",
        hit_info={"some": "data"},
    )
    cd.add_canarydrop_hit(token_hit=token_hit)
    with capturedLogs() as captured:
        webhook_channel.send_alert(
            canarydrop=cd,
            token_hit=token_hit,
            input_channel=ChannelDNS(
                switchboard=switchboard,
                settings=settings,
                backend_hostname="test.com",
                backend_scheme="https",
                listen_domain=settings.LISTEN_DOMAIN,
            ),
        )
    assert any(
        ["Failed sending request to webhook" in log["log_format"] for log in captured]
    )
