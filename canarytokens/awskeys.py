import logging
import re
from typing import Optional

import requests
from pydantic import HttpUrl

from canarytokens import tokens
from canarytokens.models import AWSKey


def validate_record(server: str, token: tokens.Canarytoken) -> bool:
    pattern = re.compile("[^a-zA-Z0-9+=,.@_-]")
    invalid_character_match = pattern.search(server)
    if invalid_character_match:
        logging.error(
            f"Hostname contains a bad character for AWS username {invalid_character_match.group(0)} ... aborting"
        )
        return False

    # Check that the full record is not too long for the DynamoDB field
    data = f"{server}@@{token.value()}"
    if len(data) > 64:
        logging.error(
            f"len({data!r}) > 64; Will not work on AWS. ",
        )
        return False
    return True


def get_aws_key(
    token: tokens.Canarytoken,
    server: str,
    aws_url: Optional[HttpUrl],
    aws_access_key_id: Optional[str],
    aws_secret_access_key: Optional[str],
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

    record = f"{server}@@{token.value()}"
    if not validate_record(server, token):
        raise ValueError(f"{record} is not valid.")

    target_url = f"{aws_url}"
    resp = requests.get(target_url, params={"data": record}, timeout=(5, 10))
    resp.raise_for_status()
    resp_json = resp.json()

    data = {
        "access_key_id": resp_json["access_key_id"],
        "secret_access_key": resp_json["secret_access_key"],
        "region": "us-east-2",
        "output": "json",
    }

    if aws_account_id := resp_json.get("aws_account_id", False):
        data["aws_account_id"] = aws_account_id

    return AWSKey(data)
