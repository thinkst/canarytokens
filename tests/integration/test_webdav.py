import easywebdav
import pytest
import requests

from canarytokens.models import (
    Memo,
    WebDavTokenHistory,
    WebDavTokenHit,
    WebDavTokenRequest,
    WebDavTokenResponse,
)
from canarytokens.settings import FrontendSettings
from pydantic import parse_obj_as, HttpUrl

from tests.utils import (
    create_token,
    get_token_history,
    server_config,
)

_TEST_WEBDAV_CLIENT_UA = "WebdavClient"
_TEST_WEBDAV_FILE_PATH = "/dir1/dir2/file.pdf"


def webdav_token_fire(token_info: WebDavTokenResponse) -> None:
    """Triggers a WebDAV token via the HTTP channel. This mimics the call made by the worker.js in Cloudflare."""
    http_url = parse_obj_as(HttpUrl, token_info.token_url)
    http_url.port = server_config.canarytokens_http_port
    url = f"{http_url.scheme}://{http_url.host}:{http_url.port}{http_url.path}"
    headers = {
        "X-Client-Ip": "128.2.4.98",
        "User-Agent": _TEST_WEBDAV_CLIENT_UA,
        "X-Alert-Path": _TEST_WEBDAV_FILE_PATH,
    }
    requests.post(url, data={}, headers=headers)


def test_webdav(
    webhook_receiver,
    frontend_settings: FrontendSettings,
):
    # initialize request
    if not frontend_settings.WEBDAV_SERVER:
        pytest.skip("The Cloudflare settings aren't present in the frontend.env")

    # from frontend.app import _create_web
    token_request_details = WebDavTokenRequest(
        webhook_url=webhook_receiver,
        memo=Memo("Testing WebDav token generation in frontend"),
        webdav_fs_type="it",
    )
    resp = create_token(token_request_details)
    token_info = WebDavTokenResponse(**resp)
    assert token_info.webdav_fs_type
    assert token_info.webdav_password
    assert token_info.webdav_server

    # Check we can browse it. This needs working Cloudflare parameters
    webdav = easywebdav.connect(
        token_info.webdav_server.split("/")[2],
        username="user",
        password=token_info.webdav_password,
        protocol="https",
    )
    assert len(webdav.ls()) > 0

    webdav_token_fire(token_info)

    token_hist_resp = get_token_history(token_info=token_info)

    token_hist = WebDavTokenHistory(**token_hist_resp)

    assert len(token_hist.hits) == 1
    assert type(token_hist.hits[0]) is WebDavTokenHit
    assert token_hist.hits[0].additional_info.file_path == _TEST_WEBDAV_FILE_PATH
    assert token_hist.hits[0].additional_info.useragent == _TEST_WEBDAV_CLIENT_UA
