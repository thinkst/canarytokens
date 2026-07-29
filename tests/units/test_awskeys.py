import json
from typing import Optional
from unittest import mock

import pytest
import requests
from pydantic import HttpUrl

from canarytokens.awskeys import enqueue_aws_id_token_deletion, get_aws_key
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.tokens import Canarytoken


@pytest.mark.parametrize(
    "path, expected_key",
    [
        (
            "mock_aws_key",
            {
                "access_key_id": "",
                "secret_access_key": "",
                "username": "awsid-test-user",
                "region": "us-east-2",
                "output": "json",
            },
        ),
        ("mock_aws_key_broken", None),
    ],
)
def test_get_aws_key_with_query(
    settings: SwitchboardSettings,
    frontend_settings: FrontendSettings,
    aws_webhook_receiver: str,
    path: str,
    expected_key: Optional[dict[str, str]],
) -> None:
    if expected_key:
        assert (
            frontend_settings.TESTING_AWS_ACCESS_KEY_ID
            and frontend_settings.TESTING_AWS_SECRET_ACCESS_KEY
        )
        expected_key["access_key_id"] = frontend_settings.TESTING_AWS_ACCESS_KEY_ID
        expected_key["secret_access_key"] = (
            frontend_settings.TESTING_AWS_SECRET_ACCESS_KEY
        )

        key = get_aws_key(
            token=Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
            server=frontend_settings.DOMAINS[0],
            auth="N/A=",
            aws_url=HttpUrl(
                f"{aws_webhook_receiver}/{path}/LinkAWSIDTokenUserToCanaryConsole"
            ),
            aws_access_key_id=None,
            aws_secret_access_key=None,
            guid="test-guid",
        )
        assert key == expected_key
    else:
        # TODO: Break these tests up. Just have 2 tests.
        with pytest.raises(requests.exceptions.HTTPError):
            key = get_aws_key(
                token=Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
                server=settings.PUBLIC_DOMAIN,
                auth="N/A=",
                aws_url=HttpUrl(
                    f"{aws_webhook_receiver}/{path}/LinkAWSIDTokenUserToCanaryConsole"
                ),
                aws_access_key_id=None,
                aws_secret_access_key=None,
            )


@pytest.mark.parametrize(
    "token, server, aws_url, aws_access_key_id, aws_secret_access_key, auth, expected_output",
    [
        (  # get mock creds you pass in yourself
            Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
            "",
            "",
            "some_access_key",
            "some_secret_key",
            "N/A=",
            {
                "access_key_id": "some_access_key",
                "secret_access_key": "some_secret_key",
                "region": "us-east-2",
                "output": "json",
            },
        ),
        (  # hit a validation error on invalid server char
            Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
            "?",
            "",
            "",
            "",
            "N/A=",
            None,
        ),
        (  # hit a ConnectionError by failing to get()
            Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
            "",
            "http://this.should.fail",
            "",
            "",
            "N/A=",
            None,
        ),
    ],
)
def test_get_aws_key_without_query(
    token: Canarytoken,
    server: str,
    aws_url: Optional[HttpUrl],
    aws_access_key_id: Optional[str],
    aws_secret_access_key: Optional[str],
    auth: str,
    expected_output: Optional[dict[str, str]],
) -> None:
    if expected_output:
        key = get_aws_key(
            token=token,
            server=server,
            auth=auth,
            aws_url=aws_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        assert key == expected_output
    else:
        with pytest.raises(Exception):
            key = get_aws_key(
                token=token,
                server=server,
                auth=auth,
                aws_url=aws_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )


def test_get_aws_key_sends_guid_and_parses_username() -> None:
    response = mock.Mock()
    response.json.return_value = {
        "access_key_id": "access-key-id",
        "secret_access_key": "secret-access-key",
        "username": "awsid-user",
    }
    aws_url = HttpUrl("https://example.com/LinkAWSIDTokenUserToCanaryConsole")
    token = Canarytoken("q9o5v58eifjf9dsn4f03sai6a")

    with mock.patch("canarytokens.awskeys.requests.get", return_value=response) as get:
        key = get_aws_key(
            token=token,
            server="example.com",
            auth="auth-token",
            aws_url=aws_url,
            aws_access_key_id=None,
            aws_secret_access_key=None,
            guid="test-guid",
        )

    get.assert_called_once_with(
        str(aws_url),
        params={
            "domain": "example.com",
            "token": token.value(),
            "auth": "auth-token",
            "guid": "test-guid",
        },
        timeout=(5, 10),
    )
    assert key["username"] == "awsid-user"


def test_enqueue_aws_id_token_deletion() -> None:
    botocore_session = mock.Mock()
    boto3_session = mock.Mock()
    sqs = mock.Mock()
    queue = mock.Mock()
    boto3_session.resource.return_value = sqs
    sqs.get_queue_by_name.return_value = queue

    with (
        mock.patch(
            "canarytokens.awskeys.botocore.session.get_session",
            return_value=botocore_session,
        ),
        mock.patch("canarytokens.awskeys.boto3.Session", return_value=boto3_session),
    ):
        enqueue_aws_id_token_deletion(
            username="awsid-user",
            canarytoken="q9o5v58eifjf9dsn4f03sai6a",
            guid="awsid-test:00000000-0000-4000-8000-000000000000",
            control_account_id="123456789012",
        )

    for config_variable in (
        "credentials_file",
        "shared_credentials_file",
        "config_file",
    ):
        botocore_session.set_config_variable.assert_any_call(config_variable, "")
    boto3_session.resource.assert_called_once_with("sqs", region_name="us-east-1")
    sqs.get_queue_by_name.assert_called_once_with(
        QueueName="awsid_delete_users_sqs",
        QueueOwnerAWSAccountId="123456789012",
    )
    message = queue.send_message.call_args.kwargs["MessageBody"]
    assert json.loads(message) == {
        "username": "awsid-user",
        "canarytoken": "q9o5v58eifjf9dsn4f03sai6a",
        "guid": "awsid-test:00000000-0000-4000-8000-000000000000",
    }
