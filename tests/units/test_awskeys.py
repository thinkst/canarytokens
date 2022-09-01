from typing import Optional

import pytest
import requests
from pydantic import HttpUrl

from canarytokens.awskeys import get_aws_key
from canarytokens.settings import Settings
from canarytokens.tokens import Canarytoken


@pytest.mark.parametrize(
    "path, expected_key",
    [
        (
            "mock_aws_key",
            {
                "access_key_id": "",
                "secret_access_key": "",
                "region": "us-east-2",
                "output": "json",
            },
        ),
        ("mock_aws_key_broken", None),
    ],
)
def test_get_aws_key_with_query(
    settings: Settings,
    webhook_receiver: str,
    path: str,
    expected_key: Optional[dict[str, str]],
) -> None:
    if expected_key:
        assert (
            settings.TESTING_AWS_ACCESS_KEY_ID
            and settings.TESTING_AWS_SECRET_ACCESS_KEY
        )
        expected_key["access_key_id"] = settings.TESTING_AWS_ACCESS_KEY_ID
        expected_key["secret_access_key"] = settings.TESTING_AWS_SECRET_ACCESS_KEY

        key = get_aws_key(
            token=Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
            server=settings.LISTEN_DOMAIN,
            aws_url=HttpUrl(
                f"{webhook_receiver}/{path}/CreateUserAPITokens",
                scheme=webhook_receiver[: webhook_receiver.index("://")],
            ),
            aws_access_key_id=None,
            aws_secret_access_key=None,
        )
        assert key == expected_key
    else:
        # TODO: Break these tests up. Just have 2 tests.
        with pytest.raises(requests.exceptions.HTTPError):
            key = get_aws_key(
                token=Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
                server=settings.LISTEN_DOMAIN,
                aws_url=HttpUrl(
                    f"{webhook_receiver}/{path}/CreateUserAPITokens",
                    scheme=webhook_receiver[: webhook_receiver.index("://")],
                ),
                aws_access_key_id=None,
                aws_secret_access_key=None,
            )


@pytest.mark.parametrize(
    "token, server, aws_url, aws_access_key_id, aws_secret_access_key, expected_output",
    [
        (  # get mock creds you pass in yourself
            Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
            "",
            "",
            "some_access_key",
            "some_secret_key",
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
            None,
        ),
        (  # hit a validation error on record too long for DynamoDB
            Canarytoken("1234567890123456789012345"),
            "678901234567890123456789012345678901",
            "none",
            "",
            "",
            None,
        ),
        (  # hit a ConnectionError by failing to get()
            Canarytoken("q9o5v58eifjf9dsn4f03sai6a"),
            "",
            "http://this.should.fail",
            "",
            "",
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
    expected_output: Optional[dict[str, str]],
) -> None:
    if expected_output:
        key = get_aws_key(
            token=token,
            server=server,
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
                aws_url=aws_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
