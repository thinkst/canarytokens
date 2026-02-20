import logging
from typing import Optional

import requests
from pydantic import HttpUrl

from canarytokens.models import CrowdStrikeCC
from canarytokens import tokens


def get_crowdstrike_key(
    token: tokens.Canarytoken,
    server: str,
    crowdstrike_url: Optional[HttpUrl] = None,
) -> CrowdStrikeCC:  # pragma: no cover
    if not (token and server) or len(server) == 0:
        logging.error("Empty values passed through to get_crowdstrike_key function.")
        raise ValueError("get_crowdstrike_key requires token and server to be set.")
    if not crowdstrike_url:
        raise ValueError(
            "get_crowdstrike_key requires crowdstrike_url to request from."
        )

    callback_url = f"https://{server}/{token.value()}"
    data = {"callback_url": callback_url}

    resp = requests.post(url=f"{crowdstrike_url}", json=data, timeout=(5, 10))
    resp.raise_for_status()
    resp_json = resp.json()

    return CrowdStrikeCC(
        token_id=resp_json["token_id"],
        client_id=resp_json["client_id"],
        client_secret=resp_json["client_secret"],
        base_url=resp_json["base_url"],
    )


def delete_crowdstrike_key(
    token_id: str,
    crowdstrike_url: Optional[HttpUrl] = None,
) -> bool:  # pragma: no cover
    if not crowdstrike_url:
        logging.warning("No CrowdStrike CC delete URL configured, skipping revocation.")
        return False

    try:
        resp = requests.post(
            url=f"{crowdstrike_url}",
            json={"token_id": token_id},
            timeout=(5, 10),
        )
        resp.raise_for_status()
        return True
    except Exception:
        logging.exception(f"Failed to delete CrowdStrike CC key")
        return False
