import os
from typing import Union
from pydantic import HttpUrl
import pytest

from canarytokens.models import (
    V2,
    V3,
    AzureIDTokenHistory,
    AzureIDTokenRequest,
    AzureIDTokenResponse,
    Memo,
    TokenTypes,
)
from canarytokens.utils import strtobool

from tests.utils import azure_token_fire, create_token
from tests.utils import get_token_history
from tests.utils import run_or_skip, v2, v3


@pytest.mark.skipif(
    strtobool(os.getenv("SKIP_AZURE_ID_TEST", "True")),
    reason="avoid using up an Azure user each time we run tests",
)
@pytest.mark.parametrize(
    "version",
    [
        v2,
        v3,
    ],
)
@pytest.mark.parametrize(
    "data,expected_hit",
    [
        (
            {
                "app_id": "some-app-id",
                "cert_id": "some-cert-id",
                "auth_details": [
                    {
                        "key": "Azure AD App Authentication Library",
                        "value": "Family: MSAL Library: MSAL.Python 1.20.0 Platform: Python",
                    }
                ],
                "ip": "1.2.3.4",
                "location": {
                    "city": "Pretoria",
                    "state": "Gauteng",
                    "countryOrRegion": "ZA",
                    "geoCoordinates": {"latitude": -25.73, "longitude": 28.21},
                },
                "resource": "Windows Azure Service Management API",
                "tenant_id": "some-tenant-id",
                "time": "2023-04-03T15:40:13.785374Z",
            },
            {
                "src_ip": "1.2.3.4",
                "additional_info": {
                    "coordinates": {"latitude": ["-25.73"], "longitude": ["28.21"]},
                    "azure_id_log_data": {
                        "Date": ["2023-04-03T15:40:13.785374Z"],
                        "Authentication": [
                            "\nAzure AD App Authentication Library: Family: MSAL Library: MSAL.Python 1.20.0 Platform: Python"
                        ],
                    },
                    "location": {
                        "city": ["Pretoria"],
                        "state": ["Gauteng"],
                        "countryOrRegion": ["ZA"],
                    },
                    "microsoft_azure": {
                        "App ID": ["some-app-id"],
                        "Resource": ["Windows Azure Service Management API"],
                        "Cert ID": ["some-cert-id"],
                    },
                },
                "input_channel": "HTTP",
            },
        )
    ],
)
def test_azure_token_post_request_processing(
    data: dict, expected_hit: dict, version: Union[V2, V3], runv2: bool, runv3: bool
):  # pragma: no cover
    """
    When an Azure Token is triggered azure makes a POST request
    back to the http channel. This is mimicked here using `azure_token_fire`.
    """
    run_or_skip(version=version, runv2=runv2, runv3=runv3)
    token_request = AzureIDTokenRequest(
        webhook_url=HttpUrl(
            "https://webhook.site/873f846e-9434-4db9-bfb4-1e7f60464f97", scheme="https"
        ),
        memo=Memo("Azure test token"),
        azure_id_cert_file_name="test_token.pem",
    )
    token_resp = create_token(
        token_request=token_request,
        version=version,
    )
    token_info = AzureIDTokenResponse(**token_resp)
    azure_token_fire(token_info=token_info, data=data, version=version)

    token_hist_resp = get_token_history(token_info=token_info, version=version)
    token_hist = AzureIDTokenHistory(**token_hist_resp)
    assert len(token_hist.hits) == 1
    hit = token_hist.hits[0]
    assert token_hist.hits[0]
    assert hit.token_type == TokenTypes.AZURE_ID
    hit_dict = hit.dict()
    for key in expected_hit:
        assert hit_dict[key] == expected_hit[key]
