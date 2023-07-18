import inspect
import json
import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from pydantic import HttpUrl

from canarytokens import canarydrop, models, queries
from canarytokens.models import (
    AnyDownloadRequest,
    AnyTokenRequest,
    AnyTokenResponse,
    AWSKeyTokenRequest,
    AWSKeyTokenResponse,
    BrowserScannerSettingsRequest,
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
    PageRequest,
    PDFTokenRequest,
    PDFTokenResponse,
    QRCodeTokenRequest,
    QRCodeTokenResponse,
    TokenTypes,
    WebhookSettingsRequest,
    WebImageSettingsRequest,
    WindowsDirectoryTokenRequest,
    WindowsDirectoryTokenResponse,
)
from canarytokens.queries import save_canarydrop
from canarytokens.settings import Settings
from canarytokens.tokens import Canarytoken
from tests.utils import get_basic_hit


def test_read_docs(test_client: TestClient) -> None:
    response = test_client.get("/docs")
    assert response.status_code == 200


def test_get_generate_page(test_client: TestClient) -> None:
    response = test_client.get("/generate")
    assert response.status_code == 200


def test_redirect_base_to_generate(test_client: TestClient) -> None:
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.url.split("/")[-1] == "generate"


def test_generate_dns_token(test_client: TestClient) -> None:
    dns_request_token = models.DNSTokenRequest(
        token_type=TokenTypes.DNS,
        email="test@test.com",
        webhook_url="https://hooks.slack.com/test",
        memo="test stuff break stuff fix stuff test stuff",
    )
    resp = test_client.post("/generate", json=json.loads(dns_request_token.json()))
    assert resp.status_code == 200


def test_generate_log4shell_token(test_client: TestClient) -> None:
    log4shell_request_token = models.Log4ShellTokenRequest(
        email="test@test.com",
        webhook_url="https://hooks.slack.com/test",
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
    CustomImageTokenRequest,
    CustomBinaryTokenRequest,
]
set_of_unsupported_response_classes = [
    CustomImageTokenResponse,
    CustomBinaryTokenResponse,
]

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
    token_request = token_request_type(
        email="test@test.com",
        webhook_url="https://hooks.slack.com/test",
        memo="test stuff break stuff fix stuff test stuff",
        redirect_url="https://youtube.com",
        clonedsite="https://test.com",
    )
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
        data=token_request_type(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
            memo="test stuff break stuff fix stuff test stuff",
            redirect_url="https://youtube.com",
            clonedsite="https://test.com",
        ).json(),
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
        data=token_request_type(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
            memo="test stuff break stuff fix stuff test stuff",
            redirect_url="https://youtube.com",
            clonedsite="https://test.com",
        ).json(),
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
        data=token_request_type(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
            memo="test stuff break stuff fix stuff test stuff",
        ).json(),
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
        data=token_request_type(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
            memo="test stuff break stuff fix stuff test stuff",
            redirect_url="https://youtube.com",
            clonedsite="https://test.com",
        ).json(),
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

    canarydrop = queries.get_canarydrop_from_auth(
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

    canarydrop = queries.get_canarydrop_from_auth(
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
        data=token_request_type(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
            memo="test stuff break stuff fix stuff test stuff",
            redirect_url="https://youtube.com",
            clonedsite="https://test.com",
        ).json(),
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

    canarydrop = queries.get_canarydrop_from_auth(
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

    canarydrop = queries.get_canarydrop_from_auth(
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
        data=token_request_type(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
            memo="test stuff break stuff fix stuff test stuff",
            redirect_url="https://youtube.com",
            clonedsite="https://test.com",
        ).json(),
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

    canarydrop = queries.get_canarydrop_from_auth(
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

    canarydrop = queries.get_canarydrop_from_auth(
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
        data=token_request_type(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
            memo="test stuff break stuff fix stuff test stuff",
            redirect_url="https://youtube.com",
            clonedsite="https://test.com",
        ).json(),
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
    canarydrop = queries.get_canarydrop_from_auth(
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
    canarydrop = queries.get_canarydrop_from_auth(
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
        data=token_request_type(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
            memo="test stuff break stuff fix stuff test stuff",
            redirect_url="https://youtube.com",
            clonedsite="https://test.com",
        ).json(),
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
        data=token_request_type(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
            memo="test stuff break stuff fix stuff test stuff",
            redirect_url="https://youtube.com",
            clonedsite="https://test.com",
            # signed_exe=UploadedExe() TODO: add support for testing these.
            # web_image=UploadedImage()
        ).json(),
    )
    token_info = token_response_type(**resp.json())

    cd = canarydrop.Canarydrop(
        type=token_info.token_type,
        canarytoken=Canarytoken(value=token_info.token),
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    save_canarydrop(cd)
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
    # TODO: Make this a stricter test
    assert cd.canarytoken.value() in resp.content.decode()


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
    param_type: PageRequest, endpoint: str, verb: str, test_client: TestClient
) -> None:
    """
    For all `endpoints` that are behind auth test
    trying to get them with invalid auth and token
    Args:
        param_type (type): Request params to use.
        endpoint (str): endpoint to attempt to access.
        verb (str): HTTP verb for endpoint.
    """
    resp = test_client.post(
        "/generate",
        data=DNSTokenRequest(
            email="test@test.com",
            webhook_url="https://hooks.slack.com/test",
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
    webhook_receiver: HttpUrl,
    settings: Settings,
    settings_env_vars: None,
    setup_db: None,
) -> None:
    aws_url = f"{webhook_receiver}/mock_aws_key_broken/CreateUserAPITokens"
    with mock.patch.dict(
        os.environ,
        {
            "CANARY_AWSID_URL": aws_url,  # backend will ask webhook_receiver for creds
            "CANARY_TESTING_AWS_ACCESS_KEY_ID": "",  # awskeys.py won't give fake creds
        },
        clear=False,
    ):
        local_settings = Settings(
            AWSID_URL=HttpUrl(aws_url, scheme=aws_url[: aws_url.index("://")]),
            TESTING_AWS_ACCESS_KEY_ID="",
            **{
                k: v
                for k, v in settings.dict().items()
                if k not in ["AWSID_URL", "TESTING_AWS_ACCESS_KEY_ID"]
            },
        )
        from backend.app import _create_aws_key_token_response

        token_request_details = AWSKeyTokenRequest(
            webhook_url=webhook_receiver,
            memo=Memo("Testing AWS Key token generation in backend"),
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
        cd.token_url = cd.get_url([canary_http_channel])
        cd.generated_hostname = cd.get_hostname()
        save_canarydrop(cd)

        resp = _create_aws_key_token_response(
            token_request_details=token_request_details,
            canarydrop=cd,
            settings=local_settings,
        )
        assert resp.status_code == 400


def test_aws_keys(
    webhook_receiver: HttpUrl,
    settings: Settings,
    settings_env_vars: None,
    setup_db: None,
) -> None:
    aws_url = f"{webhook_receiver}/mock_aws_key/CreateUserAPITokens"
    with mock.patch.dict(
        os.environ,
        {
            "CANARY_AWSID_URL": aws_url,  # backend will ask webhook_receiver for creds
            "CANARY_TESTING_AWS_ACCESS_KEY_ID": "",  # awskeys.py won't give fake creds
        },
        clear=False,
    ):
        local_settings = Settings(
            AWSID_URL=HttpUrl(aws_url, scheme=aws_url[: aws_url.index("://")]),
            TESTING_AWS_ACCESS_KEY_ID="",
            **{
                k: v
                for k, v in settings.dict().items()
                if k not in ["AWSID_URL", "TESTING_AWS_ACCESS_KEY_ID"]
            },
        )
        from backend.app import _create_aws_key_token_response

        token_request_details = AWSKeyTokenRequest(
            webhook_url=webhook_receiver,
            memo=Memo("Testing AWS Key token generation in backend"),
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
        cd.token_url = cd.get_url([canary_http_channel])
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
