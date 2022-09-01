import pytest

from canarytokens import canarydrop, queries
from canarytokens.channel import InputChannel
from canarytokens.channel_dns import ChannelDNS
from canarytokens.channel_output_webhook import WebhookOutputChannel
from canarytokens.exceptions import DuplicateChannel, InvalidChannel
from canarytokens.models import TokenTypes
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

pytestmark = pytest.mark.usefixtures("setup_db")


def test_switchboard_input_channel_check_names(settings):
    switchboard = Switchboard()
    dns_input_channel = ChannelDNS(
        switchboard=switchboard,
        settings=settings,
        listen_domain="tokens.co.za",
        backend_scheme="https",
        backend_hostname="test.com",
    )
    # switchboard.add_input_channel(name="http")
    assert dns_input_channel.name in switchboard.input_channels
    assert dns_input_channel.CHANNEL in switchboard.input_channels


@pytest.mark.asyncio(asyncio_mode="strict")
async def test_switchboard_no_channels():
    switchboard = Switchboard()
    token_hit = Canarytoken.create_token_hit(
        token_type=TokenTypes.DNS,
        input_channel="not_valid",
        hit_info={"some": "data"},
        src_ip="10.2.1.1",
    )
    with pytest.raises(InvalidChannel):
        await switchboard.dispatch(
            canarydrop=None,
            token_hit=token_hit,
        )


@pytest.mark.parametrize(
    "alert_webhook_url",
    [
        "https://hooks.slack.com/services/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",
        "https://example.com/test",
    ],
)
@pytest.mark.asyncio(asyncio_mode="strict")
async def test_switchboard_register_input_channel(settings, alert_webhook_url):
    switchboard = Switchboard()

    webhook_output_channel = WebhookOutputChannel(
        switchboard=switchboard,
        backend_hostname="test.com",
        backend_scheme="https",
    )
    switchboard.add_input_channel(
        name="tester",
        channel=InputChannel(
            switchboard=switchboard,
            name="tester",
            backend_hostname="",
            backend_scheme="",
        ),
    )
    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=TokenTypes.DNS,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=True,
        alert_webhook_url=alert_webhook_url,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
    )
    queries.save_canarydrop(cd)
    token_hit = Canarytoken.create_token_hit(
        token_type=cd.type,
        input_channel="tester",
        src_ip="127.0.0.1",
        hit_info={"some": "data"},
    )
    cd.add_canarydrop_hit(token_hit=token_hit)
    switchboard.dispatch(
        canarydrop=cd,
        token_hit=token_hit,
    )
    token_hit = Canarytoken.create_token_hit(
        token_type=cd.type,
        input_channel="tester",
        src_ip="127.0.0.1",
        hit_info={"more": "data"},
    )
    cd.add_canarydrop_hit(token_hit=token_hit)
    switchboard.dispatch(
        canarydrop=cd,
        token_hit=token_hit,
    )

    triggered_details = queries.get_canarydrop_triggered_details(canarytoken)
    assert len(triggered_details.hits) == 2

    assert webhook_output_channel.name in switchboard.output_channels
    assert webhook_output_channel.CHANNEL in switchboard.output_channels


def test_switchboard_duplicate_channel():
    switchboard = Switchboard()
    switchboard.add_output_channel("test")
    with pytest.raises(DuplicateChannel):
        switchboard.add_output_channel("test")
