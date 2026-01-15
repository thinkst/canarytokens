from tempfile import SpooledTemporaryFile

import pytest
import requests

from canarytokens.models import (
    BrowserScannerSettingsRequest,
    CustomImageTokenHistory,
    CustomImageTokenRequest,
    CustomImageTokenResponse,
    Memo,
    TokenTypes,
    UploadedImage,
    WebImageSettingsRequest,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric
from tests.utils import (
    create_token,
    get_stats_from_webhook,
    get_token_history,
    set_token_settings,
    trigger_http_token,
    server_config,
)

# the gif returned by default by the web image token
DEFAULT_GIF = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"  # 1x1 GIF


@pytest.mark.parametrize("browser_scanner_enabled", [True, False])
@pytest.mark.parametrize("web_image_enabled", [True, False])
@pytest.mark.parametrize("accept_html", [True, False])
@pytest.mark.parametrize("accept_image", [True, False])
def test_custom_image_url(  # noqa: C901
    version,
    browser_scanner_enabled,
    web_image_enabled,
    accept_html,
    accept_image,
    webhook_receiver,
    clean_uploads_dir,
):

    # custom image
    file_name = "canary_image.png"
    file_mimetype = "image/{mimetype}".format(
        mimetype=file_name[-3:].replace("jpg", "jpeg")
    )

    with open("data/{file}".format(file=file_name), "rb") as fp:
        # record contents
        input_file_contents = fp.read()
        # create SpooledTemporaryFile
        temp_file = SpooledTemporaryFile()
        temp_file.write(input_file_contents)
        temp_file.seek(0)

        # initialize request
        web_image = UploadedImage(
            filename=file_name, content_type=file_mimetype, file=temp_file
        )
        memo = "custom web token memo!"
        token_request = CustomImageTokenRequest(
            token_type=TokenTypes.WEB_IMAGE,
            web_image=web_image,
            webhook_url=webhook_receiver,
            memo=Memo(memo),
        )

        # Create custom image token
        resp = create_token(token_request=token_request)
        token_info = CustomImageTokenResponse(**resp)

        # ensure browser_scanner is enabled or not
        set_token_settings(
            setting=BrowserScannerSettingsRequest(
                value="on" if browser_scanner_enabled else "off",
                token=token_info.token,
                auth=token_info.auth_token,
            ),
        )

        # ensure web_image is enabled or not
        set_token_settings(
            setting=WebImageSettingsRequest(
                value="on" if web_image_enabled else "off",
                token=token_info.token,
                auth=token_info.auth_token,
            ),
        )

    # Check token url page extension
    assert token_info.token_url.lower().endswith((".png", ".gif", ".jpg", ".jpeg"))

    # Trigger the token alert
    accepted_content = [
        file_mimetype if accept_image else "",
        "text/html" if accept_html else "",
    ]
    _resp = trigger_http_token(
        token_info=token_info,
        headers={
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Accept": ",".join(x for x in accepted_content if x),
        },
    )

    if not accept_image and accept_html:
        # If no-image is accepted by the request and html is accepted by the request then expect html
        assert "text/html" == _resp.headers["Content-Type"]
        if browser_scanner_enabled:
            # expect browser scanner
            assert '<script type="text/javascript">' in _resp.content.decode()

        if not browser_scanner_enabled:
            # expect fortune
            assert "Pale Blue Dot" in _resp.content.decode()
    else:
        # Otherwise expect the image or the default GIF
        if web_image_enabled:
            # expect web image response
            assert file_mimetype == _resp.headers["Content-Type"]
            assert input_file_contents == _resp.content
        else:
            # expect gif response
            assert "image/gif" == _resp.headers["Content-Type"]
            assert DEFAULT_GIF == _resp.content

    # check the memo
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    # Check that the returned history has a single hit, and is on the HTTP channel
    resp = get_token_history(token_info=token_info)
    token_history = CustomImageTokenHistory(**resp)
    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "HTTP"

    if server_config.live:
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    else:
        assert token_hit.geo_info.ip == "127.0.0.1"


@pytest.mark.parametrize(
    "file_name",
    ["canary_image.png", "Moon.jpg", "testing.gif"],
)
def test_custom_image_web_image(
    version,
    file_name,
    webhook_receiver,
):

    file_mimetype = "image/{mimetype}".format(
        mimetype=file_name[-3:].replace("jpg", "jpeg")
    )
    with open("data/{file}".format(file=file_name), "rb") as fp:
        # record contents
        input_file = fp.read()

    # create SpooledTemporaryFile
    temp_file = SpooledTemporaryFile()
    temp_file.write(input_file)
    temp_file.seek(0)
    # initialize request
    web_image = UploadedImage(
        filename=file_name, content_type=file_mimetype, file=temp_file
    )
    memo = "custom web token memo!"
    token_request = CustomImageTokenRequest(
        token_type=TokenTypes.WEB_IMAGE,
        web_image=web_image,
        webhook_url=webhook_receiver,
        memo=Memo(memo),
    )

    # Create custom image token
    resp = create_token(token_request=token_request)
    token_info = CustomImageTokenResponse(**resp)

    # ensure web_image is enabled
    _res = set_token_settings(
        setting=WebImageSettingsRequest(
            value="on",
            token=token_info.token,
            auth=token_info.auth_token,
        ),
    )
    # check success of the web_image settings update
    assert _res["message"] == "success"

    # Trigger the token
    _resp = trigger_http_token(
        token_info=token_info,
        headers={
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Accept": "{mimetype}".format(
                mimetype=file_mimetype,
            ),
        },
        stream=True,
    )

    # extract incoming file's bytes
    incoming_file = _resp.content

    # compare bytes between files
    assert input_file == incoming_file

    # check the memo
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    # Check that the returned history has a single hit, and is on the HTTP channel
    resp = get_token_history(token_info=token_info)
    token_history = CustomImageTokenHistory(**resp)
    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "HTTP"
    if server_config.live:
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    else:
        assert token_hit.geo_info.ip == "127.0.0.1"


@pytest.mark.parametrize(
    "request_details, resp_details",
    [
        pytest.param(
            {"method": "GET", "headers": {}},
            {"headers": {"Access-Control-Allow-Origin": "*"}, "not_headers": []},
            id="Get-Request-Cors-Support",
        ),
        pytest.param(
            {
                "method": "OPTIONS",
                "headers": {
                    "Access-Control-Request-Method": "GET",
                    "Origin": "test.com",
                },
            },
            {
                "headers": {
                    "Access-Control-Allow-Methods": "OPTIONS, GET, POST",
                    "Access-Control-Allow-Origin": "test.com",
                },
                "not_headers": ["Access-Control-Request-Method"],
            },
            id="Preflight-Cors-Support",
        ),
        pytest.param(
            {
                "method": "OPTIONS",
                "headers": {
                    "Origin": "test.com",
                },
            },
            {
                "headers": {},
                "not_headers": [
                    "Access-Control-Allow-Methods",
                    "Access-Control-Allow-Origin",
                ],
            },
            id="Bad-Preflight-Cors-Request",
        ),
        pytest.param(
            {
                "method": "GET",
                "headers": {
                    "Access-Control-Request-Method": "GET",
                    "Origin": "test.com",
                },
            },
            {
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                },
                "not_headers": [
                    "Access-Control-Request-Method",
                    "Access-Control-Allow-Methods",
                ],
            },
            id="Get-with-Preflight-Cors-Headers",
        ),
    ],
)
def test_custom_image_web_image_cors_support(
    version, webhook_receiver, request_details, resp_details
):

    file_name = "canary_image.png"
    file_mimetype = "image/{mimetype}".format(
        mimetype=file_name[-3:].replace("jpg", "jpeg")
    )
    with open("data/{file}".format(file=file_name), "rb") as fp:
        # record contents
        input_file = fp.read()

    # create SpooledTemporaryFile
    temp_file = SpooledTemporaryFile()
    temp_file.write(input_file)
    temp_file.seek(0)
    # initialize request
    web_image = UploadedImage(
        filename=file_name, content_type=file_mimetype, file=temp_file
    )
    memo = "custom web token memo!"
    token_request = CustomImageTokenRequest(
        token_type=TokenTypes.WEB_IMAGE,
        web_image=web_image,
        webhook_url=webhook_receiver,
        memo=Memo(memo),
    )

    # Create custom image token
    resp = create_token(token_request=token_request)
    token_info = CustomImageTokenResponse(**resp)

    # ensure web_image is enabled
    _res = set_token_settings(
        setting=WebImageSettingsRequest(
            value="on",
            token=token_info.token,
            auth=token_info.auth_token,
        ),
    )
    # check success of the web_image settings update
    assert _res["message"] == "success"

    # Trigger the token
    trigger_headers = {
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Accept": "{mimetype}".format(
            mimetype=file_mimetype,
        ),
    }
    trigger_headers.update(request_details["headers"])

    _resp = trigger_http_token(
        token_info=token_info,
        headers=trigger_headers,
        stream=True,
        method=request_details["method"],
    )
    for header, value in resp_details["headers"].items():
        assert header in _resp.headers
        assert value in _resp.headers[header]

    for header in resp_details["not_headers"]:
        assert header not in _resp.headers
