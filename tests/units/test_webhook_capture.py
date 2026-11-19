from unittest.mock import Mock

import pytest
import requests
from fastapi.testclient import TestClient

from canarytokens import advocate
from canarytokens.channel_output_webhook import (
    WEBHOOK_ADDR_VALIDATOR,
    WebhookOutputChannel,
)
from canarytokens.models import TokenTypes
from canarytokens.queries import validate_webhook
from tests.utils import clear_stats_on_webhook, get_stats_from_webhook
from tests.webhook_capture import allow_capture_delivery, capture_api_url, create_app


def test_capture_isolation_and_cleanup():
    with TestClient(create_app()) as client:
        for capture_id in ("first", "second"):
            assert client.post(f"/captures/{capture_id}").status_code == 200
        assert client.post("/captures/first").status_code == 409
        client.post("/hooks/first", json={"memo": "first"})
        client.post("/hooks/second", json={"memo": "second"})
        first = client.get("/captures/first").json()["data"]
        assert len(first) == 1
        assert first[0]["headers"]["content-type"] == "application/json"
        client.delete(f"/captures/first/requests/{first[0]['uuid']}")
        assert client.get("/captures/first").json()["data"] == []
        assert len(client.get("/captures/second").json()["data"]) == 1
        client.delete("/captures/first")
        assert client.post("/hooks/first", json={}).status_code == 404
        assert client.get("/captures/first").status_code == 404


def test_real_webhook_delivery_and_helpers(webhook_receiver):
    channel = WebhookOutputChannel.__new__(WebhookOutputChannel)
    first = {
        "manage_url": "http://example.com/manage?token=first&auth=secret",
        "memo": "first",
    }
    second = {
        "manage_url": "http://example.com/manage?auth=secret&token=second",
        "memo": "second",
    }
    validate_webhook(webhook_receiver, TokenTypes.DNS)
    for payload in (first, second):
        assert channel.generic_webhook_send(payload, webhook_receiver)
    assert get_stats_from_webhook(webhook_receiver, "first") == [first]
    clear_stats_on_webhook(webhook_receiver, "first")
    assert get_stats_from_webhook(webhook_receiver, "second") == [second]
    captured = requests.get(capture_api_url(webhook_receiver), timeout=5).json()["data"]
    assert len(captured) == 1
    # The fixture must not relax the shared production validator.
    assert not WEBHOOK_ADDR_VALIDATOR.is_ip_allowed("127.0.0.1")
    with pytest.raises(advocate.exceptions.UnacceptableAddressException):
        advocate.post(
            "http://127.0.0.1:8088/unrelated", validator=WEBHOOK_ADDR_VALIDATOR
        )


def test_receiver_allowance_is_scoped():
    post = Mock()
    send = allow_capture_delivery(post, "http://127.0.0.1:8088")
    send("http://127.0.0.1:8088/hooks/test", validator=WEBHOOK_ADDR_VALIDATOR)
    kwargs = post.call_args.kwargs
    assert kwargs["validator"].is_ip_allowed("127.0.0.1")
    assert not kwargs["validator"].is_ip_allowed("127.0.0.2")
    assert kwargs["allow_redirects"] is False
    for url in ("http://127.0.0.1:8089/hooks/test", "http://127.0.0.1:8088/admin"):
        send(url, validator=WEBHOOK_ADDR_VALIDATOR)
        assert post.call_args.kwargs["validator"] is WEBHOOK_ADDR_VALIDATOR


def test_separate_capture_api_address(monkeypatch):
    monkeypatch.setenv("TEST_WEBHOOK_API_URL", "http://localhost:9000/")
    assert (
        capture_api_url("https://owned.example/hooks/test")
        == "http://localhost:9000/captures/test"
    )
