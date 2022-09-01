from typing import Sequence

import pytest
from pydantic import EmailStr
from twisted.internet.address import IPv4Address
from twisted.web.http import Request
from twisted.web.test.requesthelper import DummyChannel
from twisted.web.test.test_web import DummyRequest

from canarytokens import canarydrop, queries
from canarytokens.awskeys import get_aws_key
from canarytokens.channel_http import ChannelHTTP
from canarytokens.models import AWSKeyTokenHistory, TokenTypes
from canarytokens.settings import BackendSettings, Settings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

switchboard = Switchboard()


@pytest.mark.parametrize(
    "token_type",
    [
        TokenTypes.FAST_REDIRECT,
        TokenTypes.WEB,
    ],
)
def test_channel_http_GET(setup_db, settings, backend_settings, token_type):
    """
    Test canarytokens http (GET) channel.
    """
    http_channel = ChannelHTTP(
        backend_settings=backend_settings,
        switchboard=switchboard,
        settings=settings,
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
    request.path = cd.generate_random_url(["http://127.0.0.1:8686"])
    http_channel.canarytoken_page.render_GET(request)
    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)
    assert len(cd_updated.triggered_details.hits) == 1


@pytest.mark.parametrize(
    "token_type, request_args",
    [
        (TokenTypes.FAST_REDIRECT, {}),
        (
            TokenTypes.SLOW_REDIRECT,
            {b"l": ["https://test.com"], b"r": ["https://test.com"]},
        ),
        (
            TokenTypes.CLONEDSITE,
            {b"l": ["https://test.com"], b"r": ["https://test.com"]},
        ),
    ],
)
def test_channel_http_GET_and_POST_back(
    setup_db, backend_settings, settings, token_type, request_args
):
    """
    Test ChannelHTTP handles POST back info. SLOW_REDIRECT is
    enriched by a browser scan that POST's data back. Here we
    ensure this is added to the canarydrop.
    """
    from twisted.web.test.requesthelper import DummyChannel

    http_channel = ChannelHTTP(
        settings=settings,
        backend_settings=backend_settings,
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
    request.path = cd.generate_random_url(["http://127.0.0.1"])
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


def test_channel_http_GET_random_endpoint(setup_db, settings, backend_settings):
    """
    Test ChannelHTTP handles random non-token endpoints.
    """
    from twisted.web.test.requesthelper import DummyChannel

    http_channel = ChannelHTTP(
        backend_settings=backend_settings,
        switchboard=switchboard,
        settings=settings,
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
    )
    request.args = request_args
    request.method = b"GET"
    resp = http_channel.site.resource.render(request)
    # TODO: What should resp be? V2 is a 1x1 gif.

    cd_updated = queries.get_canarydrop(canarytoken=cd.canarytoken)

    assert len(cd_updated.triggered_details.hits) == 0
    assert cd.type == cd_updated.type

    request = Request(channel=DummyChannel())
    # TODO: Add random endpoints.
    request.path = "http://127.0.0.1/this/has/no-token"

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
        {b"last_used": [b"2022-07-29T05:48:00+00:00"], b"safety_net": [b"True"]},
    ],
)
def test_POST_aws_token_back(
    input_data: dict[bytes, Sequence[bytes]],
    backend_settings: BackendSettings,
    fake_settings_for_aws_keys: Settings,
    setup_db: None,
):
    settings = fake_settings_for_aws_keys
    http_channel = ChannelHTTP(
        settings=settings,
        backend_settings=backend_settings,
        switchboard=switchboard,
    )

    canarytoken = Canarytoken()
    key = get_aws_key(
        token=canarytoken,
        server=settings.LISTEN_DOMAIN,
        aws_url=None,  # env var might have live url, don't use up an AWS user.
        aws_access_key_id=settings.TESTING_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.TESTING_AWS_SECRET_ACCESS_KEY,
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
