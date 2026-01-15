import pytest
import requests
from http.client import OK

from canarytokens.models import (
    Memo,
    TokenTypes,
    IdPAppType,
    IdPAppTokenHistory,
    IdPAppTokenRequest,
    IdPAppTokenResponse,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric
from tests.utils import (
    create_token,
    get_stats_from_webhook,
    get_token_history,
)


@pytest.mark.parametrize(
    "redirect_url",
    ["https://canary.tools", None],
)
def test_saml_token(redirect_url, webhook_receiver):
    memo = "SAML memo!"
    token_request = IdPAppTokenRequest(
        token_type=TokenTypes.IDP_APP,
        webhook_url=webhook_receiver,
        memo=Memo(memo),
        redirect_url=redirect_url,
        app_type=IdPAppType.AWS,
    )
    resp = create_token(token_request=token_request)
    token_info = IdPAppTokenResponse(**resp)
    login_url = token_info.token_url
    entity_id = token_info.entity_id
    assert login_url.startswith(entity_id)

    with open("data/sample_saml_data.txt") as f:
        raw_text = f.read()
    data = {"SAMLResponse": [raw_text]}

    # Fire the token
    resp = requests.post(
        login_url, data, headers={"Accept": "text/html"}, timeout=(30, 30)
    )
    assert resp.status_code == OK

    # Check that the returned history has a single hit
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        TokenAlertDetailGeneric(**stats[0])

    resp = get_token_history(token_info=token_info)
    token_history = IdPAppTokenHistory(**resp)
    assert len(token_history.hits) == 1
    assert token_history.hits[0].src_data["identity"] == "tokens-testing@thinkst.com"
