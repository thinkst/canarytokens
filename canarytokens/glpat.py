from typing import Optional

import requests
from pydantic import HttpUrl, SecretStr

from canarytokens import tokens
from canarytokens.models import GLPat
from base64 import b64encode

def get_glpat(
    token: tokens.Canarytoken,
    server: str,
    gitlab_broker_url: HttpUrl,
    broker_api_key: SecretStr,
    gl_token: Optional[str],
    expires: Optional[str]
) -> GLPat:
    if gl_token and expires:
        return GLPat(
            {
                "token": gl_token,
                "expires": expires
            }
        )

    record = f"http://{server}/{token.value()}"

    target_url = f"{gitlab_broker_url}"
    resp = requests.get(target_url, params={"url": b64encode(record.encode()).decode(), "ak": broker_api_key.get_secret_value()}, timeout=(5, 10))
    resp.raise_for_status()
    resp_json = resp.json()

    pat = GLPat(
        {
            "token": resp_json["token"],
            "expires": resp_json["expires"],
        }
    )
    return pat
