"""HTTP capture service shared by local and remotely deployed test runs."""

import os
import time
from ipaddress import ip_network
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
import requests

from canarytokens import advocate


def create_app() -> FastAPI:
    app = FastAPI()
    captures = {}

    @app.post("/captures/{capture_id}")
    async def create(capture_id: str):
        if capture_id in captures:
            raise HTTPException(409, "Capture already exists")
        captures[capture_id] = []
        return {}

    @app.post("/hooks/{capture_id}")
    async def capture(capture_id: str, request: Request):
        if capture_id not in captures:
            raise HTTPException(404, "Unknown capture")
        captures[capture_id].append(
            {
                "uuid": uuid4().hex,
                "content": (await request.body()).decode("utf-8"),
                "headers": dict(request.headers),
                "timestamp": time.time(),
            }
        )
        return {}

    @app.get("/captures/{capture_id}")
    async def retrieve(capture_id: str):
        if capture_id not in captures:
            raise HTTPException(404, "Unknown capture")
        return {"data": captures[capture_id]}

    @app.delete("/captures/{capture_id}/requests/{request_id}")
    async def delete_request(capture_id: str, request_id: str):
        if capture_id not in captures:
            raise HTTPException(404, "Unknown capture")
        captures[capture_id] = [
            request for request in captures[capture_id] if request["uuid"] != request_id
        ]
        return {}

    @app.delete("/captures/{capture_id}")
    async def delete_capture(capture_id: str):
        captures.pop(capture_id, None)
        return {}

    return app


def capture_api_url(webhook_url: str) -> str:
    if urlsplit(webhook_url).hostname == "webhook.site":
        capture_id = urlsplit(webhook_url).path.strip("/")
        return f"https://webhook.site/token/{capture_id}/requests"
    base, capture_id = webhook_url.rsplit("/hooks/", 1)
    base = (os.getenv("TEST_WEBHOOK_API_URL") or base).rstrip("/")
    return f"{base}/captures/{capture_id}"


def capture_request_url(webhook_url: str, request_id: str) -> str:
    api_url = capture_api_url(webhook_url)
    if urlsplit(webhook_url).hostname == "webhook.site":
        return f"{api_url.removesuffix('/requests')}/request/{request_id}"
    return f"{api_url}/requests/{request_id}"


def create_webhook_site_url() -> str:
    for attempt in range(10):
        response = requests.post("https://webhook.site/token", timeout=30)
        if response.status_code == 429 and attempt < 9:
            time.sleep(60)
            continue
        response.raise_for_status()
        return f"https://webhook.site/{response.json()['uuid']}"
    raise RuntimeError("Failed to create webhook.site token")


def payload_token(payload: dict) -> str | None:
    query = parse_qs(urlsplit(payload.get("manage_url", "")).query)
    return query.get("token", [None])[0]


def allow_capture_delivery(post, receiver_url: str):
    """Allow only the literal receiver IP/origin in test processes, without redirects."""
    receiver = urlsplit(receiver_url)
    try:
        network = ip_network(receiver.hostname)
    except ValueError:
        return post
    validator = advocate.AddrValidator(
        ip_whitelist={network},
        port_whitelist={receiver.port or (443 if receiver.scheme == "https" else 80)},
    )

    def send(url, *args, **kwargs):
        target = urlsplit(str(url))
        if (target.scheme, target.netloc) == (
            receiver.scheme,
            receiver.netloc,
        ) and target.path.startswith(f"{receiver.path.rstrip('/')}/hooks/"):
            kwargs["validator"] = validator
            kwargs["allow_redirects"] = False
        return post(url, *args, **kwargs)

    return send
