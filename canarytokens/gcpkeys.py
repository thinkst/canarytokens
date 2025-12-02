from typing import Optional

import requests
from pydantic import HttpUrl

from canarytokens.models import GCPKey


def get_gcp_key(
    gcp_url: Optional[HttpUrl],
    gcp_auth_token: Optional[str],
    gcp_project_id: Optional[str] = None,
    gcp_private_key_id: Optional[str] = None,
) -> GCPKey:
    if gcp_private_key_id and gcp_project_id:
        return GCPKey(
            {
                "keyfile": {
                    "type": "service_account",
                    "project_id": gcp_project_id,
                    "private_key_id": gcp_private_key_id,
                    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
                    "client_email": "REDACTED",
                    "client_id": "REDACTED",
                    "auth_uri": "REDACTED",
                    "token_uri": "REDACTED",
                    "auth_provider_x509_cert_url": "REDACTED",
                    "client_x509_cert_url": "REDACTED",
                },
                "service_account_id": "REDACTED",
                "service_account_email": "REDACTED",
                "name": "REDACTED",
            }
        )

    target_url = f"{gcp_url}"
    resp = requests.get(
        target_url, params={"auth_token": gcp_auth_token}, timeout=(5, 10)
    )
    resp.raise_for_status()
    resp_json = resp.json()

    data = {
        "gcp_keyfile": resp_json["keyfile"],
        "gcp_service_account_email": resp_json["service_account_email"],
    }

    return GCPKey(data)
