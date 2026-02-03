import inspect
import json
import os
import re
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from pydantic import HttpUrl

from canarytokens import canarydrop, models, queries, constants
from canarytokens.models import (
    AWSInfraTokenRequest,
    AWSInfraTokenResponse,
    AnyDownloadRequest,
    AnyTokenRequest,
    AnyTokenResponse,
    AWSKeyTokenRequest,
    AWSKeyTokenResponse,
    AzureIDTokenRequest,
    AzureIDTokenResponse,
    BrowserScannerSettingsRequest,
    CCTokenRequest,
    CCTokenResponse,
    CustomBinaryTokenRequest,
    CustomBinaryTokenResponse,
    CustomImageTokenRequest,
    CustomImageTokenResponse,
    DNSTokenRequest,
    DNSTokenResponse,
    DownloadIncidentListCSVRequest,
    DownloadIncidentListJsonRequest,
    DownloadKubeconfigRequest,
    DownloadMSExcelRequest,
    DownloadMSWordRequest,
    DownloadMySQLRequest,
    DownloadPDFRequest,
    DownloadQRCodeRequest,
    DownloadZipRequest,
    EmailSettingsRequest,
    HistoryPageRequest,
    KubeconfigTokenRequest,
    KubeconfigTokenResponse,
    ManagePageRequest,
    Memo,
    MsExcelDocumentTokenRequest,
    MsExcelDocumentTokenResponse,
    MsWordDocumentTokenRequest,
    MsWordDocumentTokenResponse,
    MySQLTokenRequest,
    MySQLTokenResponse,
    PWATokenRequest,
    PWATokenResponse,
    PageRequest,
    PDFTokenRequest,
    PDFTokenResponse,
    QRCodeTokenRequest,
    QRCodeTokenResponse,
    TokenTypes,
    WebBugTokenRequest,
    WebhookSettingsRequest,
    WebImageSettingsRequest,
    WindowsDirectoryTokenRequest,
    WindowsDirectoryTokenResponse,
    CreditCardV2TokenRequest,
    CreditCardV2TokenResponse,
    WebDavTokenRequest,
    WebDavTokenResponse,
)
from canarytokens.queries import save_canarydrop
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.tokens import Canarytoken
from tests.utils import get_basic_hit, get_token_request
from frontend.app import ROOT_API_ENDPOINT


def test_read_docs(test_client: TestClient) -> None:
    response = test_client.get("/docs")
    assert response.status_code == 200


def test_get_generate_page(test_client: TestClient) -> None:
    response = test_client.get("/generate")
    assert response.status_code == 200


def test_redirect_base_to_generate(test_client: TestClient) -> None:
    if FrontendSettings().NEW_UI:
        pytest.skip("New UI does not redirect to /generate")
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/generate"


def test_generate_dns_token(test_client: TestClient) -> None:
    dns_request_token = models.DNSTokenRequest(
        token_type=TokenTypes.DNS,
        email="test@test.com",
        webhook_url="https://slack.com/api/api.test",
        memo="test stuff break stuff fix stuff test stuff",
    )
    resp = test_client.post("/generate", json=json.loads(dns_request_token.json()))
    assert resp.status_code == 200


def test_reject_webhook_too_long(test_client: TestClient) -> None:
    url_suffix = "a" * constants.MAX_WEBHOOK_URL_LENGTH
    dns_request_token = models.DNSTokenRequest(
        token_type=TokenTypes.DNS,
        email="test@test.com",
        webhook_url=f"https://slack.com/api/{url_suffix}",
        memo="test stuff break stuff fix stuff test stuff",
    )
    resp = test_client.post("/generate", json=json.loads(dns_request_token.json()))
    assert resp.status_code == 400


def test_generate_log4shell_token(test_client: TestClient) -> None:
    log4shell_request_token = models.Log4ShellTokenRequest(
        email="test@test.com",
        webhook_url="https://slack.com/api/api.test",
        memo="test stuff break stuff fix stuff test stuff",
    )
    resp = test_client.post(
        "/generate",
        json=json.loads(log4shell_request_token.json()),
    )
    assert resp.status_code == 200


all_classes = inspect.getmembers(models, inspect.isclass)

set_of_request_classes = sorted(
    [
        o[1]
        for o in filter(
            lambda name_class: name_class[0].endswith("TokenRequest")
            and name_class[0] != "TokenRequest",
            all_classes,
        )
    ],
    key=str,
)

set_of_response_classes = sorted(
    [
        o[1]
        for o in filter(
            lambda name_class: name_class[0].endswith("TokenResponse")
            and name_class[0] != "TokenResponse",
            all_classes,
        )
    ],
    key=str,
)

# TODO: test client uploads is not added.
# Skipping these types for now.
set_of_unsupported_request_classes = [
    AWSKeyTokenRequest,  # don't use up an AWS key
    AzureIDTokenRequest,  # don't use up an Azure ID
    CCTokenRequest,  # don't use up a CC
    CustomImageTokenRequest,
    CustomBinaryTokenRequest,
    PWATokenRequest,
    CreditCardV2TokenRequest,
    AWSInfraTokenRequest,  # no download
]
set_of_unsupported_response_classes = [
    AWSKeyTokenResponse,
    AzureIDTokenResponse,
    CCTokenResponse,
    CustomImageTokenResponse,
    CustomBinaryTokenResponse,
    PWATokenResponse,
    CreditCardV2TokenResponse,
    AWSInfraTokenResponse,  # no download
]

if not FrontendSettings("../frontend/frontend.env").WEBDAV_SERVER:
    # The Cloudflare settings for webdav aren't present
    set_of_unsupported_request_classes += [WebDavTokenRequest]
    set_of_unsupported_response_classes += [WebDavTokenResponse]

[set_of_response_classes.remove(o) for o in set_of_unsupported_response_classes]
[set_of_request_classes.remove(o) for o in set_of_unsupported_request_classes]


@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_creating_all_tokens(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
    setup_db: None,
) -> None:
    token_request = get_token_request(token_request_type)

    try:
        resp = test_client.post(
            "/generate",
            json=token_request.json_safe_dict(),
        )
    except NotImplementedError as e:
        print(f"Token {token_request_type} not implemented yet! {e}")
        raise
    else:
        assert resp.status_code == 200
        token_response_type(**resp.json())


def test_get_commit_sha(test_client: TestClient) -> None:
    resp = test_client.get("/commitsha")
    assert resp.status_code == 200


def test_get_robots_txt(test_client: TestClient) -> None:
    resp = test_client.get("/robots.txt")
    assert resp.status_code == 200
    assert resp.text.startswith("User-agent: *")
    assert "Disallow: /history" in resp.text
    assert "Disallow: /manage" in resp.text


def test_get_security_txt(test_client: TestClient) -> None:
    resp = test_client.get("/.well-known/security.txt")
    assert resp.status_code == 200
    assert (
        "Acknowledgements: https://github.com/thinkst/canarytokens/security/advisories"
        in resp.text
    )
    assert "Expires: " in resp.text
    expiry_date = re.search(r"Expires:\s*(\S+)", resp.text).group(1)
    # Check that the expiry date is in the future
    from datetime import datetime, timezone

    expiry_datetime = datetime.fromisoformat(expiry_date.replace("Z", "+00:00"))
    assert expiry_datetime > datetime.now(
        timezone.utc
    ), "Update the security.txt expiry date!"


@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_download_canarydrop_json_details(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
) -> None:
    resp = test_client.post(
        "/generate",
        data=get_token_request(token_request_type).json(),
    )
    dns_resp = token_response_type(**resp.json())
    resp_dl = test_client.get(
        "/download",
        params=DownloadIncidentListJsonRequest(
            token=dns_resp.token,
            auth=dns_resp.auth_token,
        ).dict(),
    )
    assert resp_dl.status_code == 200


@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_download_canarydrop_csv_details(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
) -> None:
    resp = test_client.post(
        "/generate",
        data=get_token_request(token_request_type).json(),
    )
    dns_resp = token_response_type(**resp.json())
    resp_dl = test_client.get(
        "/download",
        params=DownloadIncidentListCSVRequest(
            token=dns_resp.token,
            auth=dns_resp.auth_token,
        ).dict(),
    )
    assert resp_dl.status_code == 200


@pytest.mark.parametrize(
    "token_request_type, token_response_type, token_download_request_type",
    [
        (
            MsWordDocumentTokenRequest,
            MsWordDocumentTokenResponse,
            DownloadMSWordRequest,
        ),
        (
            MsExcelDocumentTokenRequest,
            MsExcelDocumentTokenResponse,
            DownloadMSExcelRequest,
        ),
        (
            WindowsDirectoryTokenRequest,
            WindowsDirectoryTokenResponse,
            DownloadZipRequest,
        ),
        (PDFTokenRequest, PDFTokenResponse, DownloadPDFRequest),
        (MySQLTokenRequest, MySQLTokenResponse, DownloadMySQLRequest),
        # (AWSKeyTokenRequest, AWSKeyTokenResponse, DownloadAWSKeysRequest),
        # (CCTokenRequest, CCTokenResponse, DownloadCCRequest),
        (KubeconfigTokenRequest, KubeconfigTokenResponse, DownloadKubeconfigRequest),
        (QRCodeTokenRequest, QRCodeTokenResponse, DownloadQRCodeRequest),
    ],
)
def test_token_download_requests(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    token_download_request_type: AnyDownloadRequest,
    test_client: TestClient,
    setup_db: None,
) -> None:
    resp = test_client.post(
        "/generate",
        data=get_token_request(token_request_type).json(),
    )
    dns_resp = token_response_type(**resp.json())
    resp_dl = test_client.get(
        "/download",
        params=token_download_request_type(
            token=dns_resp.token,
            auth=dns_resp.auth_token,
        ).dict(),
    )
    # Check that the content is at least present.
    assert len(resp_dl.content) > 20
    assert resp_dl.status_code == 200


@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_email_enable_token_settings_requests(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
) -> None:
    resp = test_client.post(
        "/generate",
        data=get_token_request(token_request_type).json(),
    )
    token_resp = token_response_type(**resp.json())

    setting_resp = test_client.post(
        "/settings",
        data=EmailSettingsRequest(
            value="off",
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
    )

    assert setting_resp.status_code == 200
    assert "success" in setting_resp.content.decode()

    canarydrop = queries.get_canarydrop_and_authenticate(
        token=token_resp.token, auth=token_resp.auth_token
    )
    assert not canarydrop.alert_email_enabled
    setting_resp = test_client.post(
        "/settings",
        data=EmailSettingsRequest(
            value="on",
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
    )

    assert setting_resp.status_code == 200
    assert "success" in setting_resp.content.decode()

    canarydrop = queries.get_canarydrop_and_authenticate(
        token=token_resp.token, auth=token_resp.auth_token
    )
    assert canarydrop.alert_email_enabled


@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_webhook_enable_token_settings_requests(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
) -> None:
    resp = test_client.post(
        "/generate",
        data=get_token_request(token_request_type).json(),
    )
    token_resp = token_response_type(**resp.json())

    setting_resp = test_client.post(
        "/settings",
        data=WebhookSettingsRequest(
            value="off",
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
    )
    assert setting_resp.status_code == 200
    assert "success" in setting_resp.content.decode()

    canarydrop = queries.get_canarydrop_and_authenticate(
        token=token_resp.token, auth=token_resp.auth_token
    )
    assert not canarydrop.alert_webhook_enabled
    setting_resp = test_client.post(
        "/settings",
        data=WebhookSettingsRequest(
            value="on",
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
    )
    assert setting_resp.status_code == 200
    assert "success" in setting_resp.content.decode()

    canarydrop = queries.get_canarydrop_and_authenticate(
        token=token_resp.token, auth=token_resp.auth_token
    )
    assert canarydrop.alert_webhook_enabled


@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_browser_scanner_enable_token_settings_requests(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
) -> None:
    resp = test_client.post(
        "/generate",
        data=get_token_request(token_request_type).json(),
    )
    token_resp = token_response_type(**resp.json())

    setting_resp = test_client.post(
        "/settings",
        data=BrowserScannerSettingsRequest(
            value="off",
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
    )

    assert setting_resp.status_code == 200
    assert "success" in setting_resp.content.decode()

    canarydrop = queries.get_canarydrop_and_authenticate(
        token=token_resp.token, auth=token_resp.auth_token
    )
    assert not canarydrop.browser_scanner_enabled
    setting_resp = test_client.post(
        "/settings",
        data=BrowserScannerSettingsRequest(
            value="on",
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
    )
    assert setting_resp.status_code == 200
    assert "success" in setting_resp.content.decode()

    canarydrop = queries.get_canarydrop_and_authenticate(
        token=token_resp.token, auth=token_resp.auth_token
    )
    assert canarydrop.browser_scanner_enabled


@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_web_image_enable_token_settings_requests(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
) -> None:
    resp = test_client.post(
        "/generate",
        data=get_token_request(token_request_type).json(),
    )
    token_resp = token_response_type(**resp.json())

    setting_resp = test_client.post(
        "/settings",
        data=WebImageSettingsRequest(
            value="off",
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
    )
    assert setting_resp.status_code == 200
    assert "success" in setting_resp.content.decode()
    canarydrop = queries.get_canarydrop_and_authenticate(
        token=token_resp.token, auth=token_resp.auth_token
    )
    assert not canarydrop.web_image_enabled
    setting_resp = test_client.post(
        "/settings",
        data=WebImageSettingsRequest(
            value="on",
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
    )
    assert setting_resp.status_code == 200
    assert "success" in setting_resp.content.decode()
    canarydrop = queries.get_canarydrop_and_authenticate(
        token=token_resp.token, auth=token_resp.auth_token
    )
    assert canarydrop.web_image_enabled


@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_canarydrop_manage_page(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
    setup_db: None,
) -> None:
    resp = test_client.post(
        "/generate",
        data=get_token_request(token_request_type).json(),
    )
    token_resp = token_response_type(**resp.json())
    manage_resp = test_client.get(
        "/manage",
        params=ManagePageRequest(
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
    )
    assert manage_resp.status_code == 200


@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_history_page(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
) -> None:
    resp = test_client.post(
        "/generate",
        data=get_token_request(token_request_type).json(),
    )
    token_info = token_response_type(**resp.json())

    token = Canarytoken(token_info.token)
    cd = queries.get_canarydrop(token)

    hit = get_basic_hit(cd.type)
    cd.add_canarydrop_hit(token_hit=hit)

    resp = test_client.get(
        "/history",
        params=HistoryPageRequest(
            token=token_info.token,
            auth=token_info.auth_token,
        ).dict(),
    )
    assert resp.status_code == 200
    # now that it's a Vue app we can't test further here


@pytest.mark.parametrize(
    "param_type, endpoint, verb",
    [
        (HistoryPageRequest, "/history", "get"),
        (ManagePageRequest, "/manage", "get"),
        (EmailSettingsRequest, "/settings", "post"),
        (DownloadIncidentListJsonRequest, "/download", "get"),
    ],
)
def test_authorised_page_access(
    param_type: PageRequest, endpoint: str, verb: str, test_client: TestClient, setup_db
) -> None:
    """
    For all `endpoints` that are behind auth test
    trying to get them with invalid auth and token
    Args:
        param_type (type): Request params to use.
        endpoint (str): endpoint to attempt to access.
        verb (str): HTTP verb for endpoint.
    """
    if FrontendSettings().NEW_UI:
        pytest.skip("New UI redirects these to index.html")
    resp = test_client.post(
        "/generate",
        data=DNSTokenRequest(
            email="test@test.com",
            webhook_url="https://slack.com/api/api.test",
            memo="test stuff break stuff fix stuff test stuff",
            redirect_url="https://youtube.com",
            clonedsite="https://test.com",
        ).json(),
    )
    token_info = DNSTokenResponse(**resp.json())

    resp = getattr(test_client, verb)(
        endpoint,
        params=param_type(
            token=token_info.token[::-1],
            auth=token_info.auth_token,
        ).dict(),
    )
    assert resp.status_code == 403

    resp = getattr(test_client, verb)(
        endpoint,
        params=param_type(
            token=token_info.token,
            auth=token_info.auth_token[::-1],
        ).dict(),
    )
    assert resp.status_code == 403


def test_aws_keys_broken(
    aws_webhook_receiver: HttpUrl,
    frontend_settings: FrontendSettings,
    settings_env_vars: None,
    setup_db: None,
) -> None:
    aws_url = f"{aws_webhook_receiver}/mock_aws_key_broken/CreateUserAPITokens"
    with mock.patch.dict(
        os.environ,
        {
            "CANARY_AWSID_URL": aws_url,  # frontend will ask aws_webhook_receiver for creds
            "CANARY_TESTING_AWS_ACCESS_KEY_ID": "",  # awskeys.py won't give fake creds
        },
        clear=False,
    ):
        local_settings = FrontendSettings(
            AWSID_URL=HttpUrl(aws_url, scheme=aws_url[: aws_url.index("://")]),
            TESTING_AWS_ACCESS_KEY_ID="",
            **{
                k: v
                for k, v in frontend_settings.dict().items()
                if k not in ["AWSID_URL", "TESTING_AWS_ACCESS_KEY_ID"]
            },
        )
        from frontend.app import _create_aws_key_token_response

        token_request_details = AWSKeyTokenRequest(
            webhook_url=aws_webhook_receiver,
            memo=Memo("Testing AWS Key token generation in frontend"),
        )

        canarytoken = Canarytoken()
        cd = canarydrop.Canarydrop(
            type=token_request_details.token_type,
            alert_email_enabled=False,
            alert_webhook_enabled=True,
            alert_webhook_url=token_request_details.webhook_url,
            canarytoken=canarytoken,
            memo=token_request_details.memo,
        )

        # add generate random hostname an token
        canary_http_channel = f"http://{local_settings.DOMAINS[0]}"
        cd.get_url([canary_http_channel])
        cd.generated_hostname = cd.get_hostname()
        save_canarydrop(cd)

        resp = _create_aws_key_token_response(
            token_request_details=token_request_details,
            canarydrop=cd,
            settings=local_settings,
        )
        assert resp.status_code == 400


def test_aws_keys(
    aws_webhook_receiver: HttpUrl,
    settings: SwitchboardSettings,
    frontend_settings: FrontendSettings,
    settings_env_vars: None,
    setup_db: None,
) -> None:
    aws_url = f"{aws_webhook_receiver}/mock_aws_key/CreateUserAPITokens"
    with mock.patch.dict(
        os.environ,
        {
            "CANARY_AWSID_URL": aws_url,  # frontend will ask webhook_receiver for creds
            "CANARY_TESTING_AWS_ACCESS_KEY_ID": "",  # awskeys.py won't give fake creds
        },
        clear=False,
    ):
        local_settings = FrontendSettings(
            AWSID_URL=HttpUrl(aws_url, scheme=aws_url[: aws_url.index("://")]),
            TESTING_AWS_ACCESS_KEY_ID="",
            **{
                k: v
                for k, v in frontend_settings.dict().items()
                if k not in ["AWSID_URL", "TESTING_AWS_ACCESS_KEY_ID"]
            },
        )
        from frontend.app import _create_aws_key_token_response

        token_request_details = AWSKeyTokenRequest(
            webhook_url=aws_webhook_receiver,
            memo=Memo("Testing AWS Key token generation in frontend"),
        )

        canarytoken = Canarytoken()
        cd = canarydrop.Canarydrop(
            type=token_request_details.token_type,
            alert_email_enabled=False,
            alert_webhook_enabled=True,
            alert_webhook_url=token_request_details.webhook_url,
            canarytoken=canarytoken,
            memo=token_request_details.memo,
        )

        # add generate random hostname an token
        canary_http_channel = f"http://{local_settings.DOMAINS[0]}"
        cd.get_url([canary_http_channel])
        cd.generated_hostname = cd.get_hostname()
        save_canarydrop(cd)

        resp = _create_aws_key_token_response(
            token_request_details=token_request_details,
            canarydrop=cd,
            settings=local_settings,
        )

        token_info = AWSKeyTokenResponse(**resp.dict())
        assert token_info.aws_secret_access_key
        assert token_info.region == "us-east-2"
        assert token_info.output == "json"


@pytest.fixture(scope="function")
def frontend_settings_with_webdav(
    frontend_settings: FrontendSettings,
):
    overrides = {
        "WEBDAV_SERVER": "https://examplewebdavserver.com",
        "CLOUDFLARE_ACCOUNT_ID": "nosuchaccountid",
        "CLOUDFLARE_API_TOKEN": "nosuchapitoken",
        "CLOUDFLARE_NAMESPACE": "nosuchnamespace",
    }
    yield next(
        enumerate(_frontend_settings_with_overrides(frontend_settings, overrides))
    )[1]


@pytest.fixture(scope="function")
def frontend_settings_with_no_webdav(frontend_settings: FrontendSettings):
    overrides = {
        "WEBDAV_SERVER": "",
        "CLOUDFLARE_ACCOUNT_ID": "",
        "CLOUDFLARE_API_TOKEN": "",
        "CLOUDFLARE_NAMESPACE": "",
    }
    yield next(
        enumerate(_frontend_settings_with_overrides(frontend_settings, overrides))
    )[1]


def _frontend_settings_with_overrides(
    frontend_settings: FrontendSettings, overrides: dict
):
    with mock.patch.dict(
        os.environ,
        {"CANARY_" + k: v for (k, v) in overrides.items()},
        clear=False,
    ):
        local_settings = frontend_settings.dict()
        for k, v in overrides.items():
            local_settings[k] = v
        local_settings = FrontendSettings(**local_settings)
        yield local_settings


def test_webdav(
    webhook_receiver: HttpUrl,
    frontend_settings_with_webdav,
    setup_db: None,
) -> None:
    """
    Test that the creation flow returns a correctly formatted Canarydrop object.

    It mocks out creating a corresponding object at Cloudflare, because this is a unit test.
    """

    from frontend.app import _create_webdav_token_response

    token_request_details = WebDavTokenRequest(
        webhook_url=webhook_receiver,
        memo=Memo("Testing WebDav token generation in frontend"),
        webdav_fs_type="it",
    )

    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=token_request_details.token_type,
        alert_email_enabled=False,
        alert_webhook_enabled=True,
        alert_webhook_url=token_request_details.webhook_url,
        canarytoken=canarytoken,
        memo=token_request_details.memo,
    )

    # add generate random hostname an token
    canary_http_channel = f"http://{frontend_settings_with_webdav.DOMAINS[0]}"
    cd.get_url([canary_http_channel])
    cd.generated_hostname = cd.get_hostname()

    import frontend.app  # noqa: F401

    with mock.patch("frontend.app.insert_webdav_token", return_value=True):
        resp = _create_webdav_token_response(
            token_request_details=token_request_details,
            canarydrop=cd,
            settings=frontend_settings_with_webdav,
        )

    token_info = WebDavTokenResponse(**resp.dict())
    assert token_info.webdav_fs_type == "it"
    assert re.match(r"^[a-f0-9]{40}$", token_info.webdav_password)
    assert token_info.webdav_server == "https://examplewebdavserver.com"


def test_webdav_no_cloudflare(
    webhook_receiver: HttpUrl,
    frontend_settings_with_no_webdav,
    setup_db,
) -> None:
    """
    Test whether a Canarytokens instance with no Network Folder enabled returns the correct response.
    """
    from frontend.app import _create_webdav_token_response

    token_request_details = WebDavTokenRequest(
        webhook_url=webhook_receiver,
        memo=Memo("Testing WebDav token generation in frontend"),
        webdav_fs_type="it",
    )

    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=token_request_details.token_type,
        alert_email_enabled=False,
        alert_webhook_enabled=True,
        alert_webhook_url=token_request_details.webhook_url,
        canarytoken=canarytoken,
        memo=token_request_details.memo,
    )
    # add generate random hostname an token
    canary_http_channel = f"http://{frontend_settings_with_no_webdav.DOMAINS[0]}"
    cd.get_url([canary_http_channel])
    cd.generated_hostname = cd.get_hostname()

    resp = _create_webdav_token_response(
        token_request_details=token_request_details,
        canarydrop=cd,
        settings=frontend_settings_with_no_webdav,
    )
    assert resp.status_code == 400
    assert (
        b"This Canarytokens instance does not have the Network Folder Canarytoken enabled."
        in resp.body
    )


@pytest.mark.parametrize(
    "block_target, test_target",
    [
        ("a@b.c", "a@b.c"),
        ("a+b@gmail.com", "a+c@gmail.com"),
        ("c.com", "b@c.com"),
    ],
)
def test_block_user(
    block_target,
    test_target,
    test_client: TestClient,
    setup_db: None,
) -> None:
    # block clock_target
    (block_func, unblock_func) = [
        (queries.block_domain, queries.unblock_domain),
        (queries.block_email, queries.unblock_email),
    ]["@" in block_target]
    block_func(block_target)

    # try to make with test_target, make sure it fails
    token_request = WebBugTokenRequest(
        email=test_target,
        webhook_url="https://slack.com/api/api.test",
        memo="test stuff break stuff fix stuff test stuff",
        redirect_url="https://youtube.com",
        clonedsite="https://test.com",
        cmd_process="klist.exe",
    )

    resp = test_client.post(
        "/generate",
        json=token_request.json_safe_dict(),
    )
    assert resp.json()["error"] == "6"

    # unblock and try again, make sure it works
    unblock_func(block_target)

    resp = test_client.post(
        "/generate",
        json=token_request.json_safe_dict(),
    )
    assert not resp.json()["error"]


@pytest.mark.parametrize(
    "headers, expected_headers",
    [
        pytest.param(
            {
                "x-real-ip": "127.0.300.1",
                "x-forwarded-for": "127.0.400.1",
            },
            {
                "created_from_ip": "127.0.300.1",
                "created_from_ip_x_forwarded_for": "127.0.400.1",
            },
            id="ValidHeaders",
        ),
        pytest.param(
            {},
            {
                "created_from_ip": "",
                "created_from_ip_x_forwarded_for": "",
            },
            id="EmptyHeaders",
        ),
    ],
)
@pytest.mark.parametrize(
    "token_request_type, token_response_type",
    zip(set_of_request_classes, set_of_response_classes),
)
def test_generate_token_ip_headers(
    token_request_type: AnyTokenRequest,
    token_response_type: AnyTokenResponse,
    test_client: TestClient,
    setup_db: None,
    headers: dict[str, str],
    expected_headers: dict[str, str],
) -> None:
    resp = test_client.post(
        "/generate", data=get_token_request(token_request_type).json(), headers=headers
    )
    token_resp = token_response_type(**resp.json())
    manage_resp = test_client.get(
        f"{ROOT_API_ENDPOINT}/manage",
        params=ManagePageRequest(
            token=token_resp.token,
            auth=token_resp.auth_token,
        ).dict(),
        follow_redirects=True,
    )
    assert manage_resp.status_code == 200
    canarydrop = manage_resp.json()["canarydrop"]
    for key, value in expected_headers.items():
        assert canarydrop[key] == value
