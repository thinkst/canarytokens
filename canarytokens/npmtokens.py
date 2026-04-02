import io
import json
import textwrap
import zipfile
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote

import requests
from pydantic import HttpUrl

from canarytokens import queries, tokens
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import NPMPublishToken, NPMPublishTokenHit, TokenTypes
from canarytokens.switchboard import Switchboard


def get_npm_publish_token(
    token: tokens.Canarytoken,
    server: str,
    npm_create_url: Optional[HttpUrl],
) -> NPMPublishToken:
    if not npm_create_url:
        raise ValueError("get_npm_publish_token requires npm_create_url to be set.")

    callback_url = f"https://{server}/{token.value()}"
    resp = requests.post(
        url=f"{npm_create_url}",
        json={"callback_url": callback_url},
        timeout=(5, 10),
    )
    resp.raise_for_status()
    data = resp.json()
    return NPMPublishToken(
        token=data["token"],
        token_id=data["token_id"],
        package_name=data["package_name"],
        package_version=data["package_version"],
    )


def delete_npm_publish_token(
    token_id: str, npm_delete_url: Optional[HttpUrl] = None
) -> bool:
    if not npm_delete_url:
        return False
    try:
        resp = requests.post(
            url=f"{npm_delete_url}", json={"token_id": token_id}, timeout=(5, 10)
        )
        resp.raise_for_status()
        return True
    except Exception:
        return False


def make_npm_publish_workspace(
    package_name: str, package_version: str, canarytoken: str
) -> bytes:
    package_json = json.dumps(
        {
            "name": package_name,
            "version": package_version,
            "description": f"Canarytokens npm publish canary {canarytoken}",
            "main": "index.js",
            "files": ["index.js"],
            "license": "UNLICENSED",
        },
        indent=2,
    )
    index_js = "module.exports = { canary: true };\n"
    npmrc = "//registry.npmjs.org/:_authToken=${NPM_TOKEN}\n"
    readme = textwrap.dedent(
        f"""
        # npm publish canary

        Package: `{package_name}`
        Version to publish: `{package_version}`

        1. Export the token as `NPM_TOKEN`
        2. Run `npm publish --access public`
        """
    ).lstrip()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        root = package_name.split("/")[-1]
        zf.writestr(f"{root}/package.json", package_json)
        zf.writestr(f"{root}/index.js", index_js)
        zf.writestr(f"{root}/.npmrc", npmrc)
        zf.writestr(f"{root}/README.md", readme)
    return buf.getvalue()


def _has_been_triggered(canarydrop: Canarydrop) -> bool:
    return any(
        getattr(hit, "npm_package_version", None) == canarydrop.npm_package_version
        for hit in canarydrop.triggered_details.hits
    )


def poll_npm_publish_canarydrops(
    switchboard: Switchboard, npm_delete_url: Optional[HttpUrl] = None
) -> int:
    hits = 0
    for canarydrop in queries.get_canarydrops_by_type(TokenTypes.NPM_PUBLISH):
        try:
            if (
                not canarydrop.npm_package_name
                or not canarydrop.npm_package_version
                or _has_been_triggered(canarydrop)
            ):
                continue

            package_name = quote(canarydrop.npm_package_name, safe="")
            resp = requests.get(
                f"https://registry.npmjs.org/{package_name}", timeout=(5, 10)
            )
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            versions = resp.json().get("versions", {})
            if canarydrop.npm_package_version not in versions:
                continue

            token_hit = NPMPublishTokenHit(
                time_of_hit=datetime.now(timezone.utc).timestamp(),
                src_ip="registry.npmjs.org",
                geo_info=None,
                is_tor_relay=False,
                input_channel="HTTP",
                src_data=None,
                useragent=None,
                npm_package_name=canarydrop.npm_package_name,
                npm_package_version=canarydrop.npm_package_version,
            )
            canarydrop.add_canarydrop_hit(token_hit=token_hit)
            switchboard.dispatch(canarydrop=canarydrop, token_hit=token_hit)
            if canarydrop.npm_token_id:
                delete_npm_publish_token(
                    token_id=canarydrop.npm_token_id, npm_delete_url=npm_delete_url
                )
            hits += 1
        except Exception:
            continue
    return hits
