import difflib
from tempfile import SpooledTemporaryFile

import pytest
import requests

from canarytokens.models import (
    V2,
    V3,
    BrowserScannerSettingsRequest,
    CustomImageTokenHistory,
    CustomImageTokenRequest,
    CustomImageTokenResponse,
    Memo,
    TokenAlertDetailGeneric,
    TokenTypes,
    UploadedImage,
    WebImageSettingsRequest,
)
from tests.utils import (
    create_token,
    get_stats_from_webhook,
    get_token_history,
    run_or_skip,
    set_token_settings,
    trigger_http_token,
    v2,
    v3,
)

# the gif returned by default by the web image token
DEFAULT_GIF = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"  # 1x1 GIF


@pytest.mark.parametrize("version", [v2, v3])
@pytest.mark.parametrize("browser_scanner_enabled", [True, False])
@pytest.mark.parametrize("web_image_enabled", [True, False])
@pytest.mark.parametrize("accept_html", [True, False])
def test_custom_image_url(  # noqa: C901
    version,
    browser_scanner_enabled,
    web_image_enabled,
    accept_html,
    webhook_receiver,
    runv2,
    runv3,
    clean_uploads_dir,
):
    run_or_skip(version, runv2=runv2, runv3=runv3)
    # custom image
    file_name = "canary_image.png"
    file_mimetype = "image/{mimetype}".format(mimetype=file_name[-3:])

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
        resp = create_token(token_request=token_request, version=version)
        token_info = CustomImageTokenResponse(**resp)

        # ensure browser_scanner is enabled or not
        set_token_settings(
            setting=BrowserScannerSettingsRequest(
                value="on" if browser_scanner_enabled else "off",
                token=token_info.token,
                auth=token_info.auth_token,
            ),
            version=version,
        )

        # ensure web_image is enabled or not
        set_token_settings(
            setting=WebImageSettingsRequest(
                value="on" if web_image_enabled else "off",
                token=token_info.token,
                auth=token_info.auth_token,
            ),
            version=version,
        )

    # Trigger the token alert
    _resp = trigger_http_token(
        token_info=token_info,
        version=version,
        headers={
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Accept": "image/gif,{mimetype}{html_type}".format(
                mimetype=file_mimetype, html_type=",text/html" if accept_html else ""
            ),
        },
    )

    # check response
    if browser_scanner_enabled and accept_html:
        # expect browser scanner response
        assert "text/html" == _resp.headers["Content-Type"]
        assert '<script type="text/javascript">' in _resp.content.decode()

    if web_image_enabled and not accept_html:
        # expect web image response
        assert file_mimetype == _resp.headers["Content-Type"]
        assert input_file_contents == _resp.content

    if not web_image_enabled and not accept_html:
        # expect gif response
        assert "image/gif" == _resp.headers["Content-Type"]
        assert DEFAULT_GIF == _resp.content

    if not browser_scanner_enabled and web_image_enabled and accept_html:
        # expect fortune or gif or image response
        assert (
            file_mimetype == _resp.headers["Content-Type"]
            or "image/gif" == _resp.headers["Content-Type"]
            or "text/html" == _resp.headers["Content-Type"]
        )
        assert (
            input_file_contents == _resp.content
            or DEFAULT_GIF == _resp.content
            or "<title>Fortune</title>" in _resp.content.decode()
        )

    if not browser_scanner_enabled and not web_image_enabled and accept_html:
        # expect fortune or gif response
        assert (
            "image/gif" == _resp.headers["Content-Type"]
            or "text/html" == _resp.headers["Content-Type"]
        )
        assert (
            DEFAULT_GIF == _resp.content
            or "<title>Fortune</title>" in _resp.content.decode()
        )

    # check the memo

    if web_image_enabled and not accept_html:
        # expect web image response
        assert file_mimetype == _resp.headers["Content-Type"]
        assert input_file_contents == _resp.content

    if not web_image_enabled and not accept_html:
        # expect gif response
        assert "image/gif" == _resp.headers["Content-Type"]
        assert DEFAULT_GIF == _resp.content

    if not browser_scanner_enabled and web_image_enabled and accept_html:
        # expect fortune or gif or image response
        assert (
            file_mimetype == _resp.headers["Content-Type"]
            or "image/gif" == _resp.headers["Content-Type"]
            or "text/html" == _resp.headers["Content-Type"]
        )
        assert (
            input_file_contents == _resp.content
            or DEFAULT_GIF == _resp.content
            or "<title>Fortune</title>" in _resp.content.decode()
        )

    if not browser_scanner_enabled and not web_image_enabled and accept_html:
        # expect fortune or gif response
        assert (
            "image/gif" == _resp.headers["Content-Type"]
            or "text/html" == _resp.headers["Content-Type"]
        )
        assert (
            DEFAULT_GIF == _resp.content
            or "<title>Fortune</title>" in _resp.content.decode()
        )

    # check the memo

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    # Check that the returned history has a single hit, and is on the HTTP channel
    resp = get_token_history(token_info=token_info, version=version)
    token_history = CustomImageTokenHistory(**resp)
    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "HTTP"

    if version.live:
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    else:
        assert token_hit.geo_info.ip == "127.0.0.1"


@pytest.mark.parametrize("version", [v2, v3])
@pytest.mark.parametrize(
    "file_name",
    ["canary_image.png", "Moon.jpg", "testing.gif"],
)
def test_custom_image_web_image(
    version,
    file_name,
    webhook_receiver,
    runv2,
    runv3,
    # clean_uploads_dir
):
    run_or_skip(version, runv2=runv2, runv3=runv3)

    file_mimetype = "image/{mimetype}".format(mimetype=file_name[-3:])
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
        resp = create_token(token_request=token_request, version=version)
        token_info = CustomImageTokenResponse(**resp)

        # ensure web_image is enabled
        _res = set_token_settings(
            setting=WebImageSettingsRequest(
                value="on",
                token=token_info.token,
                auth=token_info.auth_token,
            ),
            version=version,
        )
        # check success of the web_image settings update
        if isinstance(version, V2):
            assert _res["result"] == "success"
        elif isinstance(version, V3):
            assert _res["message"] == "success"

        # Trigger the token
        _resp = trigger_http_token(
            token_info=token_info,
            version=version,
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

        # compare file lengths
        assert len(input_file) == len(incoming_file)

        # comapare bytes between files
        num_diffs = 0
        difference = difflib.Differ().compare(input_file, incoming_file)
        for diff in difference:
            # no match if diff starts with "-"
            if diff.startswith("-"):
                num_diffs = num_diffs + 1
        assert num_diffs == 0

    # check the memo

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    # Check that the returned history has a single hit, and is on the HTTP channel
    resp = get_token_history(token_info=token_info, version=version)
    token_history = CustomImageTokenHistory(**resp)
    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "HTTP"
    if version.live:
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    else:
        assert token_hit.geo_info.ip == "127.0.0.1"
