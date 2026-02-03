import json
import requests
from typing import Optional
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum  # Python 3.11+
else:
    from backports.strenum import StrEnum  # Python < 3.11
from hashlib import sha1

from canarytokens.settings import FrontendSettings

settings = FrontendSettings()

ACCOUNT_ID = settings.CLOUDFLARE_ACCOUNT_ID
NAMESPACE_ID = settings.CLOUDFLARE_NAMESPACE


# Matches the keys in the worker's fs.js
class FsType(StrEnum):
    TESTING = "testing"
    SECURITY = "security"
    DEFENSE = "defense"
    MEDICAL = "medical"
    IT = "it"


def generate_webdav_password(
    token_id: str, server_domain: str = settings.DOMAINS[0]
) -> str:
    return sha1((server_domain + token_id).encode()).hexdigest()


def insert_webdav_token(
    password: str,
    alert_url: str,
    webdav_fs_type: Optional[FsType] = None,
    custom_fs: Optional[str] = None,
) -> bool:
    """
    Inserts a token config into the Cloudflare KV store
    Returns: True if successful, False otherwise
    """
    value = {"token_url": alert_url}

    if webdav_fs_type is not None:
        value["fs_template"] = f"{webdav_fs_type}"
    if custom_fs is not None:
        value["custom_fs"] = custom_fs

    fd = {"value": json.dumps(value), "metadata": "{}"}
    put_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{NAMESPACE_ID}/values/{password}"
    res = requests.put(
        put_url,
        files=fd,
        headers={"Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}"},
    )
    if res.status_code == 200:
        return True
    else:
        print(res.text)
        return False
