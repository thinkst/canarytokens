import io
from unittest import mock
import zipfile

from pydantic import HttpUrl

from canarytokens.npmtokens import (
    get_npm_publish_token,
    make_npm_publish_workspace,
    poll_npm_publish_canarydrops,
)
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import TokenTypes
from canarytokens.queries import delete_canarydrop, get_canarydrop, save_canarydrop
from canarytokens.tokens import Canarytoken


def test_get_npm_publish_token() -> None:
    response = mock.Mock()
    response.json.return_value = {
        "token": "npm-test-token",
        "token_id": "npm-test-token-id",
        "package_name": "@thinkst/canary-test",
        "package_version": "0.0.2",
    }
    response.raise_for_status.return_value = None

    with mock.patch("canarytokens.npmtokens.requests.post", return_value=response) as post:
        token = get_npm_publish_token(
            token=Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
            server="canarytokens.org",
            npm_create_url=HttpUrl("https://example.com/create", scheme="https"),
        )

    assert token["package_name"] == "@thinkst/canary-test"
    assert (
        post.call_args.kwargs["json"]["callback_url"]
        == "https://canarytokens.org/q9o5v58eifjf9dsn4f03sai6a"
    )


def test_make_npm_publish_workspace() -> None:
    workspace = make_npm_publish_workspace(
        package_name="@thinkst/canary-test",
        package_version="0.0.2",
        canarytoken="test-token",
    )

    with zipfile.ZipFile(io.BytesIO(workspace)) as zf:
        assert "canary-test/package.json" in zf.namelist()
        assert "canary-test/.npmrc" in zf.namelist()
        assert b"${NPM_TOKEN}" in zf.read("canary-test/.npmrc")
        assert b'"version": "0.0.2"' in zf.read("canary-test/package.json")


def test_poll_npm_publish_canarydrops(setup_db) -> None:
    canarytoken = Canarytoken()
    canarydrop = Canarydrop(
        type=TokenTypes.NPM_PUBLISH,
        alert_email_enabled=True,
        alert_email_recipient="test@test.com",
        alert_webhook_enabled=True,
        alert_webhook_url="https://slack.com/api/api.test",
        canarytoken=canarytoken,
        memo="test npm publish canary",
        browser_scanner_enabled=False,
        npm_token="npm-test-token",
        npm_token_id="npm-test-token-id",
        npm_package_name="@thinkst/canary-test",
        npm_package_version="0.0.2",
    )
    save_canarydrop(canarydrop)

    response = mock.Mock()
    response.status_code = 200
    response.json.return_value = {"versions": {"0.0.2": {}}}
    response.raise_for_status.return_value = None
    switchboard = mock.Mock()

    with mock.patch("canarytokens.npmtokens.requests.get", return_value=response), mock.patch(
        "canarytokens.npmtokens.delete_npm_publish_token"
    ) as delete_token:
        hits = poll_npm_publish_canarydrops(
            switchboard=switchboard,
            npm_delete_url=HttpUrl("https://example.com/delete", scheme="https"),
        )

    updated_canarydrop = get_canarydrop(canarytoken=canarytoken)
    assert hits == 1
    assert updated_canarydrop.triggered_details.hits[0].npm_package_version == "0.0.2"
    switchboard.dispatch.assert_called_once()
    delete_token.assert_called_once_with(
        token_id="npm-test-token-id",
        npm_delete_url=HttpUrl("https://example.com/delete", scheme="https"),
    )


def test_delete_canarydrop_revokes_npm_publish_token(setup_db) -> None:
    canarydrop = Canarydrop(
        type=TokenTypes.NPM_PUBLISH,
        alert_email_enabled=False,
        alert_webhook_enabled=False,
        canarytoken=Canarytoken(),
        memo="test npm publish delete",
        browser_scanner_enabled=False,
        npm_token_id="npm-test-token-id",
    )
    save_canarydrop(canarydrop)

    with mock.patch.dict(
        "os.environ",
        {"CANARY_NPM_PUBLISH_DELETE_URL": "https://example.com/delete"},
        clear=False,
    ), mock.patch("canarytokens.npmtokens.delete_npm_publish_token") as delete_token:
        delete_canarydrop(canarydrop)

    delete_token.assert_called_once_with(
        token_id="npm-test-token-id",
        npm_delete_url=HttpUrl("https://example.com/delete", scheme="https"),
    )
