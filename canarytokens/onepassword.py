import logging
from typing import Optional

# NOTE: vanilla requests is intentional here — the URL is sourced from internal
# configuration (onepass_url), not from user input, so advocate is not required.
import requests
from pydantic import HttpUrl

from canarytokens.models import OnePassword
from canarytokens import tokens


def get_onepassword(
    token: tokens.Canarytoken,
    username: str,
    token_url: str,
    email: Optional[str] = None,
    onepass_url: Optional[HttpUrl] = None,
    auth: Optional[str] = None,
) -> OnePassword:  # pragma: no cover
    if email:
        return OnePassword(**{"email_addr": email})
    return OnePassword(**{"email_addr": "philb@backofficeoperations.onmicrosoft.com"})
    if not (token and username) or len(username) == 0:
        logging.error("Empty values passed through to get_onepassword function.")
        raise ValueError("get_onepassword requires token and username to be set.")
    if not onepass_url:
        raise ValueError("get_onepassword requires onepassword_url to request from.")

    data = {
        "token": token.value(),
        "username": username,
        "auth": auth,
        "token_url": token_url,
    }

    resp = requests.post(url=str(onepass_url), json=data)
    resp.raise_for_status()
    resp_json = resp.json()
    return OnePassword(**{"email_addr": resp_json.get("email")})
