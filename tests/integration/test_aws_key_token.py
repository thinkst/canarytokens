import os
from time import sleep
from typing import Dict, Union

import boto3
import botocore.exceptions
import pytest
import requests
from pydantic import HttpUrl

from canarytokens.models import (
    V2,
    V3,
    AWSKeyTokenHistory,
    AWSKeyTokenRequest,
    AWSKeyTokenResponse,
    DownloadIncidentListJsonRequest,
    Memo,
    TokenTypes,
)
from canarytokens.utils import strtobool

from tests.utils import aws_token_fire, create_token
from tests.utils import get_token_history as utils_get_token_history
from tests.utils import run_or_skip, v3


def get_token_history(token_info, version) -> Dict[str, str]:  # pragma: no cover
    token_history_request = DownloadIncidentListJsonRequest(
        token=token_info.token,
        # TODO: auth vs. auth_token choose one at least at the object level
        auth=token_info.auth_token,
        fmt="incidentlist_json",
    )
    resp = requests.get(
        url=f"{version.server_url}/download",
        params=token_history_request.dict(),
    )
    if resp.status_code == 404:
        return {}
    elif resp.status_code == 200:
        data = resp.json()
        data["token_type"] = data.get("token_type", None) or token_info.token_type
        return data
    else:
        resp.raise_for_status()


@pytest.mark.parametrize("version", [v3])
@pytest.mark.skipif(
    (
        strtobool(os.getenv("SKIP_AWS_KEY_TEST", "True"))
        or not strtobool(os.getenv("LIVE", "False"))
    ),
    reason="avoid using up an AWS user each time we run tests, and AWS can't trigger unless live",
)
def test_aws_key_token(version, webhook_receiver, runv2, runv3):  # pragma: no cover
    run_or_skip(version, runv2=runv2, runv3=runv3)

    # Make the token
    token_request = AWSKeyTokenRequest(
        webhook_url=HttpUrl(url=webhook_receiver, scheme="https"),
        memo=Memo("Test stuff break stuff test stuff sometimes build stuff"),
    )
    resp = create_token(token_request, version=version)
    token_info = AWSKeyTokenResponse(**resp)

    # Make sure the downloaded version is what we expect
    url = f"http://{version.canarytokens_domain}/download?fmt=awskeys&token={token_info.token}&auth={token_info.auth_token}&encoded=false"
    raw_creds = requests.get(url).content.decode("utf-8")
    print(f"creds:\n{raw_creds}")
    [_, AKI, SAK, region, output] = raw_creds.strip().split("\n")
    # TODO: the text output is `aws_access_key_id`, not `aws_access_key`,
    #       so we should check if the latter should be changed.
    assert AKI == f"aws_access_key={token_info.aws_access_key_id}"
    assert SAK == f"aws_secret_access_key={token_info.aws_secret_access_key}"
    assert region == f"region={token_info.region}"
    assert output == f"output={token_info.output}"

    # Trigger the token
    session = boto3.Session(
        aws_access_key_id=token_info.aws_access_key_id,
        aws_secret_access_key=token_info.aws_secret_access_key,
    )
    sts = session.client("sts")

    caller_identity = {}
    caller_id_wait = 0
    while not caller_identity:
        try:
            caller_identity = sts.get_caller_identity()
        except botocore.exceptions.ClientError:
            print("\n\nfailed to authenticate. sleeping 5 and trying again.\n\n")
            sleep(5)
            caller_id_wait += 5
        if caller_id_wait > 1 * 60:
            assert False, "timed out on sts.get_caller_identity() retries"
    print("\n\nauthenticated with sts.\n\n")

    assert "UserId" in caller_identity

    # Check that the returned history has a single hit
    history_resp = get_token_history(token_info, version=version)
    history_wait = 0
    while not history_resp:
        sleep(5)
        history_wait += 5
        history_resp = get_token_history(token_info, version=version)
        if history_wait > 20 * 60:
            assert False, "timed out waiting for trigger to register in history"
    token_history = AWSKeyTokenHistory(**history_resp)

    assert len(token_history.hits) == 1


@pytest.mark.skipif(
    (
        strtobool(os.getenv("SKIP_AWS_KEY_TEST", "True"))
        or not strtobool(os.getenv("LIVE", "False"))
    ),
    reason="avoid using up an AWS user each time we run tests, and AWS can't trigger unless live",
)
@pytest.mark.parametrize(
    "version",
    [
        v3,
    ],
)
def test_aws_token_post_request_processing(
    version: Union[V2, V3], runv2, runv3
):  # pragma: no cover
    """When an AWS Token is triggered a lambda makes a POST request
    back to the http channel. This is tested here using `aws_token_fire`
    which run code akin to the lambda.
    TODO: make the lambda and this test (`def aws_token_fire(...)`) share code.
    """
    run_or_skip(version=version, runv2=runv2, runv3=runv3)
    token_resp = create_token(
        token_request=AWSKeyTokenRequest(
            email="test@test.com",
            memo="Aws test token",
        ),
        version=version,
    )
    token_info = AWSKeyTokenResponse(**token_resp)
    # Fire aws token
    aws_token_fire(token_info=token_info, version=version)

    token_hist_resp = utils_get_token_history(token_info=token_info, version=version)

    token_hist = AWSKeyTokenHistory(**token_hist_resp)
    assert len(token_hist.hits) == 1
    hit = token_hist.hits[0]
    assert token_hist.hits[0]
    assert hit.additional_info.aws_key_log_data["eventName"] == ["GetCallerIdentity"]
    assert hit.token_type == TokenTypes.AWS_KEYS
