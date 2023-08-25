# pytest caplog
from twisted.logger import capturedLogs

from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import format_as_googlechat_canaryalert
from canarytokens.channel_dns import ChannelDNS
from canarytokens.channel_output_webhook import WebhookOutputChannel
from canarytokens.models import TokenAlertDetailsGoogleChat, TokenTypes
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken


def test_broken_webhook(
    setup_db,
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
):
    switchboard = Switchboard()
    switchboard.switchboard_settings = settings
    webhook_channel = WebhookOutputChannel(
        switchboard=switchboard,
        switchboard_scheme=settings.SWITCHBOARD_SCHEME,
        frontend_domain="test.com",
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
                frontend_settings=frontend_settings,
                switchboard_hostname="test.com",
                switchboard_scheme=settings.SWITCHBOARD_SCHEME,
            ),
        )
    assert any(
        ["Failed connecting to webhook" in log["log_format"] for log in captured]
    )


def test_webhook(
    setup_db,
    webhook_receiver,
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
):
    switchboard = Switchboard()
    webhook_channel = WebhookOutputChannel(
        switchboard=switchboard,
        switchboard_scheme=settings.SWITCHBOARD_SCHEME,
        frontend_domain="test.com",
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
                frontend_settings=frontend_settings,
                switchboard_hostname="test.com",
                switchboard_scheme=settings.SWITCHBOARD_SCHEME,
            ),
        )
    assert any(["Successfully sent to " in log["log_format"] for log in captured])


def test_googlechat_webhook_format(
    setup_db,
    webhook_receiver,
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
):

    switchboard = Switchboard()
    input_channel = ChannelDNS(
        switchboard=switchboard,
        frontend_settings=frontend_settings,
        switchboard_hostname="test.com",
        switchboard_scheme=settings.SWITCHBOARD_SCHEME,
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
    details = input_channel.gather_alert_details(
        cd,
        protocol=input_channel.switchboard_scheme,
        host=settings.PUBLIC_DOMAIN,
    )
    print("Webhook details = {}".format(details))
    webhook_payload = format_as_googlechat_canaryalert(details=details)
    webhook_payload_json = webhook_payload.json_safe_dict()
    print("Webhook_payload json = {}".format(webhook_payload.json()))

    assert "cardsV2" in webhook_payload_json.keys()
    assert type(webhook_payload_json["cardsV2"]) is list
    assert len(webhook_payload_json["cardsV2"]) == 1
    for key in ["cardId", "card"]:
        assert key in webhook_payload_json["cardsV2"][0].keys()
    assert type(webhook_payload_json["cardsV2"][0]["cardId"]) is str
    assert type(webhook_payload_json["cardsV2"][0]["card"]) is dict
    for key in ["header", "sections"]:
        assert key in webhook_payload_json["cardsV2"][0]["card"].keys()
    assert type(webhook_payload_json["cardsV2"][0]["card"]["header"]) is dict
    for key in ["title", "imageUrl", "imageType", "imageAltText"]:
        assert key in webhook_payload_json["cardsV2"][0]["card"]["header"].keys()
        assert type(webhook_payload_json["cardsV2"][0]["card"]["header"][key]) is str
    assert type(webhook_payload_json["cardsV2"][0]["card"]["sections"]) is list
    assert len(webhook_payload_json["cardsV2"][0]["card"]["sections"]) == 2
    assert type(webhook_payload_json["cardsV2"][0]["card"]["sections"][0]) is dict
    for key in ["header", "collapsible", "widgets"]:
        assert key in webhook_payload_json["cardsV2"][0]["card"]["sections"][0].keys()
    assert (
        type(webhook_payload_json["cardsV2"][0]["card"]["sections"][0]["header"]) is str
    )
    assert (
        type(webhook_payload_json["cardsV2"][0]["card"]["sections"][0]["collapsible"])
        is bool
    )
    assert (
        type(webhook_payload_json["cardsV2"][0]["card"]["sections"][0]["widgets"])
        is list
    )
    assert type(webhook_payload_json["cardsV2"][0]["card"]["sections"][1]) is dict
    for key in ["header", "collapsible", "widgets"]:
        assert key in webhook_payload_json["cardsV2"][0]["card"]["sections"][1].keys()


def test_canaryalert_googlechat_webhook(
    setup_db,
    webhook_receiver,
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
):
    """
    Tests if a google chat webhook payload, is produced given a googlechat webhook receiver.
    """
    googlechat_webhook_receiver = (
        "https://chat.googleapis.com/v1/spaces/random/messages?key=temp_key"
    )

    switchboard = Switchboard()
    input_channel = ChannelDNS(
        switchboard=switchboard,
        frontend_settings=frontend_settings,
        switchboard_hostname=frontend_settings.DOMAINS[0],
        switchboard_scheme=settings.SWITCHBOARD_SCHEME,
    )

    cd = Canarydrop(
        type=TokenTypes.DNS,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=googlechat_webhook_receiver,
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

    canaryalert_webhook_payload = input_channel.format_webhook_canaryalert(
        canarydrop=cd,
        protocol=input_channel.switchboard_scheme,
        host=input_channel.hostname,
    )
    assert isinstance(canaryalert_webhook_payload, TokenAlertDetailsGoogleChat)
