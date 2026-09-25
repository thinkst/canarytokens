import logging
from typing import Optional

# NOTE: vanilla requests is intentional here — the URL is sourced from internal
# configuration (onepass_url), not from user input, so advocate is not required.
import requests
from pydantic import HttpUrl

from canarytokens.models import OnePassword
from canarytokens import tokens

log = logging.getLogger("uvicorn")


def get_one_password(
    token: tokens.Canarytoken,
    username: str,
    token_url: str,
    email: Optional[str] = None,
    onepass_url: Optional[HttpUrl] = None,
    auth: Optional[str] = None,
) -> OnePassword:  # pragma: no cover
    if email:
        return OnePassword(**{"email_addr": email})

    if not (token_url and username) or len(username) == 0:
        log.error("Empty values passed through to get_one_password function.")
        raise ValueError("get_one_password requires token and username to be set.")
    if onepass_url is None:
        log.error("No onepass_url value passed through to get_one_password function.")
        raise ValueError("get_one_password requires one_password_url to request from.")

    data = {
        "token": token,
        "username": username,
        "auth": auth,
        "token_url": token_url,
    }
    resp = requests.post(url=str(onepass_url), json=data)
    resp.raise_for_status()
    resp_json = resp.json()
    return OnePassword(**{"email_addr": resp_json.get("email_addr")})
