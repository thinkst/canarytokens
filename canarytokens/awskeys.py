import json
import logging
import re
from typing import Optional

import boto3
import botocore

# NOTE: vanilla requests is intentional here — the URL is sourced from internal
# configuration (aws_url), not from user input, so advocate is not required.
import requests
from pydantic import HttpUrl

from canarytokens import tokens
from canarytokens.models import AWSKey


AWSID_DELETE_USERS_QUEUE_NAME = "awsid_delete_users_sqs"


def validate_record(server: str, token: tokens.Canarytoken) -> bool:
    # Check `server` has no invalid characters (NB: a match here *is* an error)
    pattern = re.compile("[^a-zA-Z0-9+=,.@_-]")
    invalid_character_match = pattern.search(server)
    if invalid_character_match:
        logging.error(
            f"Hostname contains a bad character for AWS username {invalid_character_match.group(0)} ... aborting"
        )
        return False

    return True


def get_aws_key(
    token: tokens.Canarytoken,
    server: str,
    auth: Optional[str],
    aws_url: Optional[HttpUrl],
    aws_access_key_id: Optional[str],
    aws_secret_access_key: Optional[str],
    guid: Optional[str] = None,
) -> AWSKey:
    if aws_secret_access_key and aws_access_key_id:
        return AWSKey(
            {
                "access_key_id": aws_access_key_id,
                "secret_access_key": aws_secret_access_key,
                "region": "us-east-2",
                "output": "json",
            }
        )

    if not validate_record(server, token):
        raise ValueError(f"{server} is not valid.")

    target_url = f"{aws_url}"
    params = {"domain": server, "token": token.value(), "auth": auth}
    if guid:
        params["guid"] = guid

    resp = requests.get(target_url, params=params, timeout=(5, 10))
    resp.raise_for_status()
    resp_json = resp.json()

    data = {
        "access_key_id": resp_json["access_key_id"],
        "secret_access_key": resp_json["secret_access_key"],
        "username": resp_json["username"],
        "region": "us-east-2",
        "output": "json",
    }

    if aws_account_id := resp_json.get("aws_account_id", False):
        data["aws_account_id"] = aws_account_id

    return AWSKey(data)


def enqueue_aws_id_token_deletion(
    username: str,
    canarytoken: str,
    guid: str,
    control_account_id: str,
) -> None:
    payload = {
        "username": username,
        "canarytoken": canarytoken,
        "guid": guid,
    }

    botocore_session = botocore.session.get_session()
    botocore_session.set_config_variable("credentials_file", "")
    botocore_session.set_config_variable("shared_credentials_file", "")
    botocore_session.set_config_variable("config_file", "")
    session = boto3.Session(botocore_session=botocore_session)

    sqs = session.resource("sqs", region_name="us-east-1")
    queue = sqs.get_queue_by_name(
        QueueName=AWSID_DELETE_USERS_QUEUE_NAME,
        QueueOwnerAWSAccountId=control_account_id,
    )
    queue.send_message(MessageBody=json.dumps(payload))
