from typing import Sequence

import json
import pytest
import io
from pydantic import EmailStr
from twisted.internet.address import IPv4Address
from twisted.web.http import Request
from twisted.web.test.requesthelper import DummyChannel
from twisted.web.test.test_web import DummyRequest

from canarytokens import canarydrop, queries
from canarytokens.awskeys import get_aws_key
from canarytokens.channel_http import ChannelHTTP
from canarytokens.models import (
    AWSKeyTokenHistory,
    TokenTypes,
    CreditCardV2TokenHit,
    CreditCardV2TokenHistory,
)
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

switchboard = Switchboard()


@pytest.mark.parametrize(
    "token_type",
    [
        TokenTypes.FAST_REDIRECT,
        TokenTypes.WEB,
        TokenTypes.WEB_IMAGE,
    ],
)
def test_channel_http_GET(setup_db, settings, frontend_settings, token_type):
    """
    Test canarytokens http (GET) channel.
    """
    http_channel = ChannelHTTP(
        switchboard=switchboard,
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
    )

    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=token_type,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    queries.save_canarydrop(cd)

    client = IPv4Address(type="TCP", host="127.0.0.1", port=8686)
    request = DummyRequest("/")
    request.client = client
    request.uri = cd.generate_random_url(["http://127.0.0.1:8686"]).encode()
    request.path = request.uri[request.uri.index(b"/", 8) :]  # noqa: E203
    http_channel.canarytoken_page.render_GET(request)
    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)
    assert len(cd_updated.triggered_details.hits) == 1


def test_channel_http_GET_token_limit(setup_db, settings, frontend_settings):
    """
    Test canarytokens http (GET) channel.
    """
    http_channel = ChannelHTTP(
        switchboard=switchboard,
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
    )

    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=TokenTypes.WEB,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    queries.save_canarydrop(cd)

    client = IPv4Address(type="TCP", host="127.0.0.1", port=8686)
    request = DummyRequest("/")
    request.client = client
    request.uri = cd.generate_random_url(["http://127.0.0.1:8686"]).encode()
    request.path = request.uri[request.uri.index(b"/", 8) :]  # noqa: E203
    for _ in range(100):
        http_channel.canarytoken_page.render_GET(request)
    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)
    assert len(cd_updated.triggered_details.hits) == settings.MAX_HISTORY


@pytest.mark.parametrize(
    "token_type, request_args",
    [
        (TokenTypes.FAST_REDIRECT, {}),
        (
            TokenTypes.SLOW_REDIRECT,
            {b"l": [b"https://test.com"], b"r": [b"https://test.com"]},
        ),
        (
            TokenTypes.CLONEDSITE,
            {b"l": [b"https://test.com"], b"r": [b"https://test.com"]},
        ),
    ],
)
def test_channel_http_GET_and_POST_back(
    setup_db, frontend_settings, settings, token_type, request_args
):
    """
    Test ChannelHTTP handles POST back info. SLOW_REDIRECT is
    enriched by a browser scan that POST's data back. Here we
    ensure this is added to the canarydrop.
    """
    from twisted.web.test.requesthelper import DummyChannel

    http_channel = ChannelHTTP(
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
        switchboard=switchboard,
    )
    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=token_type,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    queries.save_canarydrop(cd)

    request = Request(channel=DummyChannel())
    request.uri = cd.generate_random_url(["http://127.0.0.1:8686"]).encode()
    request.path = request.uri[request.uri.index(b"/", 8) :]  # noqa: E203
    request.args = request_args
    request.method = b"GET"
    http_channel.site.resource.render(request)

    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)
    assert len(cd_updated.triggered_details.hits) == 1
    assert cd.type == cd_updated.type

    if token_type == TokenTypes.SLOW_REDIRECT:
        data_1 = {
            b"key": [cd_updated.triggered_details.hits[-1].time_of_hit],
            b"canarytoken": cd_updated.canarytoken.value(),
            b"name": [b"Browser"],
            b"enabled": [b"1"],
            b"installed": [b"1"],
            b"browser": [b"Chrome"],
            b"version": [b"99.0.4844.84"],
            b"mimetypes": [b""],
            b"language": [b"en-US"],
            b"platform": [b"MacIntel"],
            b"vendor": [b"Google Inc."],
            b"os": [b"Macintosh"],
        }

        request = Request(channel=DummyChannel())
        request.path = cd.generate_random_url(["http://127.0.0.1"])

        request.args = request_args | data_1
        request.method = b"POST"

        http_channel.site.resource.render(request)
        cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)
        # Check that Slow redirect post enriches the initial hit.
        assert len(cd_updated.triggered_details.hits) == 1
        assert cd.type == cd_updated.type
        assert (
            cd_updated.triggered_details.hits[0].additional_info.browser.browser[0]
            == data_1[b"browser"][0].decode()
        )


@pytest.mark.parametrize(
    "token_type",
    [
        TokenTypes.WEB,
        TokenTypes.WEB_IMAGE,
        TokenTypes.SLOW_REDIRECT,
    ],
)
def test_channel_http_POST(setup_db, frontend_settings, settings, token_type):
    """
    Test canarytokens http (POST) channel.
    """
    from twisted.web.test.requesthelper import DummyChannel

    http_channel = ChannelHTTP(
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
        switchboard=switchboard,
    )
    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=token_type,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    queries.save_canarydrop(cd)

    request = Request(channel=DummyChannel())
    request.uri = cd.generate_random_url(["http://127.0.0.1:8686"]).encode()
    request.path = request.uri[request.uri.index(b"/", 8) :]  # noqa: E203

    request.args = {
        b"browser": [b"Chrome"],
        b"something1": [b"value1"],
        b"something2": [b"1234"],
    }

    request.method = b"POST"
    http_channel.site.resource.render(request)

    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)
    assert len(cd_updated.triggered_details.hits) == 1
    assert cd.type == cd_updated.type


def test_channel_http_GET_random_endpoint(setup_db, settings, frontend_settings):
    """
    Test ChannelHTTP handles random non-token endpoints.
    """
    from twisted.web.test.requesthelper import DummyChannel

    http_channel = ChannelHTTP(
        switchboard=switchboard,
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
    )
    token_type, request_args = TokenTypes.FAST_REDIRECT, {}
    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=token_type,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    queries.save_canarydrop(cd)

    request = Request(channel=DummyChannel())
    # TODO: Add random endpoints.
    request.path = "//".join(
        cd.generate_random_url(["http://127.0.0.1"]).split("/")[::2][:2]
    ).encode()
    request.args = request_args
    request.method = b"GET"
    resp = http_channel.site.resource.render(request)
    # TODO: What should resp be? V2 is a 1x1 gif.

    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)

    assert len(cd_updated.triggered_details.hits) == 0
    assert cd.type == cd_updated.type

    request = Request(channel=DummyChannel())
    # TODO: Add random endpoints.
    request.path = b"http://127.0.0.1/this/has/no-token"

    request.args = request_args
    request.method = b"POST"
    resp = http_channel.site.resource.render(request)
    assert resp == b"failed"

    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)

    assert len(cd_updated.triggered_details.hits) == 0
    assert cd.type == cd_updated.type


@pytest.mark.parametrize(
    "input_data",
    [
        {
            b"ip": [b"172.253.205.33"],
            b"user_agent": [
                b"Boto3/1.20.46 Python/3.9.10 Darwin/21.4.0 Botocore/1.23.46"
            ],
            b"eventName": [b"GetCallerIdentity"],
        },
        {
            b"last_used": [b"2022-07-29T05:48:00+00:00"],
            b"safety_net": [b"True"],
            b"last_used_service": [b"sts"],
        },
    ],
)
def test_POST_aws_token_back(
    input_data: dict[bytes, Sequence[bytes]],
    frontend_settings: FrontendSettings,
    fake_settings_for_aws_keys: SwitchboardSettings,
    setup_db: None,
):
    settings = fake_settings_for_aws_keys
    http_channel = ChannelHTTP(
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
        switchboard=switchboard,
    )

    canarytoken = Canarytoken()
    key = get_aws_key(
        token=canarytoken,
        server=settings.PUBLIC_DOMAIN,
        aws_url=None,  # env var might have live url, don't use up an AWS user.
        aws_access_key_id=frontend_settings.TESTING_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=frontend_settings.TESTING_AWS_SECRET_ACCESS_KEY,
    )

    if not key:
        raise ValueError("Failed to get aws key")

    cd = canarydrop.Canarydrop(
        type=TokenTypes.AWS_KEYS,
        triggered_details=AWSKeyTokenHistory(),
        alert_email_enabled=False,
        alert_email_recipient=EmailStr("email@test.com"),
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        aws_access_key_id=key["access_key_id"],
        aws_secret_access_key=key["secret_access_key"],
        aws_region=key["region"],
        aws_output=key["output"],
    )
    queries.save_canarydrop(cd)

    request = Request(channel=DummyChannel())
    request.path = f"http://127.0.0.1/{canarytoken.value()}".encode()

    data = input_data
    request.args = data
    request.method = b"POST"

    http_channel.site.resource.render(request)

    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)

    assert cd_updated is not None
    assert len(cd_updated.triggered_details.hits) == 1
    if b"safety_net" not in request.args:
        assert cd_updated.triggered_details.hits[0].additional_info.aws_key_log_data[
            "eventName"
        ] == ["GetCallerIdentity"]
    assert cd.type == cd_updated.type


@pytest.mark.parametrize(
    "trigger_type,webhook_data_extra",
    [
        (
            "issuing.transaction.failed",
            {
                "transaction_date": "2025-02-03T00:42:00Z",
                "transaction_type": "PURCHASE",
                "status": "DECLINED",
            },
        ),
        (
            "issuing.3ds_notification.stepup_otp",
            {},
        ),
    ],
)
def test_POST_cc_token_v2_back(
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
    setup_db: None,
    trigger_type: str,
    webhook_data_extra: dict,
):
    """
    Test the v2 credit card token webhook. Verifies that transaction data
    is captured correctly in the token alert for both transaction failure and 3DS
    notification webhooks.
    """

    http_channel = ChannelHTTP(
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
        switchboard=switchboard,
    )

    canarytoken = Canarytoken()

    cd = canarydrop.Canarydrop(
        type=TokenTypes.CREDIT_CARD_V2,
        triggered_details=CreditCardV2TokenHistory(),
        alert_email_enabled=False,
        alert_email_recipient=EmailStr("email@test.com"),
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
    )
    queries.save_canarydrop(cd)

    webhook_url = cd.get_url(
        [f"{frontend_settings.DOMAINS[0]}:{settings.CHANNEL_HTTP_PORT}"]
    )

    merchant_identifier = "MID123456789"
    merchant_name = "ACME Airline Co."
    merchant_city = "New York"
    merchant_country = "US"
    masked_card = "**** **** **** 1234"
    amount = "6.39"
    currency = "USD"

    webhook_data = {
        "trigger_type": trigger_type,
        "canarytoken": canarytoken.value(),
        "masked_card_number": masked_card,
        "transaction_amount": amount,
        "transaction_currency": currency,
        "merchant_detail": {
            "identifier": merchant_identifier,
            "name": merchant_name,
            "city": merchant_city,
            "country": merchant_country,
        },
        **webhook_data_extra,
    }

    request = Request(channel=DummyChannel())
    request.uri = webhook_url.encode()
    request.path = request.uri[request.uri.index(b"/", 8) :]  # noqa: E203
    request.method = b"POST"
    request.content = io.BytesIO(json.dumps(webhook_data).encode())

    http_channel.site.resource.render(request)

    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)
    assert cd_updated is not None
    assert len(cd_updated.triggered_details.hits) == 1
    assert cd.type == cd_updated.type

    hit = cd_updated.triggered_details.hits[0]
    assert isinstance(hit, CreditCardV2TokenHit)
    hit_info = hit.additional_info

    assert hit_info.merchant_identifier == merchant_identifier
    assert hit_info.masked_card_number == masked_card
    assert hit_info.transaction_amount == amount
    assert hit_info.transaction_currency == currency
    assert hit_info.merchant == f"{merchant_name}, {merchant_city}, {merchant_country}"

    if trigger_type == "issuing.transaction.failed":
        assert hit_info.transaction_date == webhook_data_extra["transaction_date"]
        assert hit_info.transaction_type == webhook_data_extra["transaction_type"]
        assert hit_info.status == webhook_data_extra["status"]


def test_channel_http_OPTIONS(setup_db, settings, frontend_settings):
    """
    Alert triggers on HTTP OPTIONS request to Canarytokens HTTP channel
    """
    http_channel = ChannelHTTP(
        switchboard=switchboard,
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
    )

    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=TokenTypes.WEB,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
    )
    queries.save_canarydrop(cd)

    client = IPv4Address(type="TCP", host="127.0.0.1", port=8686)
    request = DummyRequest("/")
    request.client = client
    request.uri = cd.generate_random_url(["http://127.0.0.1:8686"]).encode()
    request.path = request.uri[request.uri.index(b"/", 8) :]  # noqa: E203
    resp = http_channel.canarytoken_page.render_OPTIONS(request)
    assert isinstance(resp, bytes), "HTTP Channel did not return bytes"
    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)
    assert len(cd_updated.triggered_details.hits) == 1


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_channel_http_ignored_ip(setup_db, http_channel, method):
    """
    Test ignored IPs on canarytokens http channel.
    """
    cd = create_canarydrop(token_type=TokenTypes.WEB)

    cd.set_ignored_ip_addresses(ip_addresses=["127.0.0.1"])

    request = create_dummy_request(cd)
    render_method = getattr(http_channel.canarytoken_page, f"render_{method}")
    render_method(request)

    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)
    assert len(cd_updated.triggered_details.hits) == 1
    assert cd_updated.triggered_details.hits[0].ignored is True


def create_canarydrop(token_type="web") -> canarydrop.Canarydrop:
    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=token_type,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
    )

    queries.save_canarydrop(cd)
    return cd


def delete_canarydrop(cd: canarydrop.Canarydrop) -> None:
    queries.delete_canarydrop(canarydrop=cd)


def create_dummy_request(cd: canarydrop.Canarydrop) -> DummyRequest:
    client = IPv4Address(type="TCP", host="127.0.0.1", port=8686)
    request = DummyRequest("/")
    request.client = client
    request.uri = cd.generate_random_url(["http://127.0.0.1:8686"]).encode()
    request.path = request.uri[request.uri.index(b"/", 8) :]  # noqa: E203
    return request


@pytest.fixture(scope="module")
def http_channel(
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
) -> ChannelHTTP:
    http_channel = ChannelHTTP(
        switchboard=switchboard,
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
    )
    return http_channel
