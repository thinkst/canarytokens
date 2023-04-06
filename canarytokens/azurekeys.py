import logging
from typing import Optional

import requests
from pydantic import HttpUrl

from canarytokens.models import AzureID
from canarytokens import tokens


def get_azure_id(
    token: tokens.Canarytoken,
    server: str,
    cert_file_name: str,
    azure_url: Optional[HttpUrl] = None,
    app_id: Optional[str] = None,
    cert: Optional[str] = None,
    tenant_id: Optional[str] = None,
    cert_name: Optional[str] = None,
) -> AzureID:
    if app_id and cert and tenant_id and cert_name:
        return AzureID(
            **{
                "app_id": app_id,
                "cert": cert,
                "tenant_id": tenant_id,
                "cert_name": cert_name,
                "cert_file_name": cert_file_name,
            }
        )
    if not (token and server) or len(server) == 0:
        logging.error("Empty values passed through to get_azure_id function.")
        raise ValueError("get_azure_id requires token and server to be set.")
    if not azure_url:
        raise ValueError("get_azure_id requires azure_url to request from.")

    data = {"token": token.value(), "domain": server}

    resp = requests.post(url=azure_url, json=data)
    resp.raise_for_status()
    resp_json = resp.json()
    return AzureID(
        **{
            "app_id": resp_json["app_id"],
            "cert": resp_json["cert"],
            "tenant_id": resp_json["tenant_id"],
            "cert_name": resp_json["cert_name"],
            "cert_file_name": cert_file_name,
        }
    )
