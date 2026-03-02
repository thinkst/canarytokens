"""
SSRF and DNS-rebinding protection — WebhookOutputChannel integration tests.

Purpose
-------
These tests verify that the production webhook alert path uses advocate to
block SSRF and DNS-rebinding attacks end-to-end, from token hit through to
the outbound HTTP call.

They complement:
  - tests/units/test_ssrf_advocate_baseline.py  (advocate in isolation)
  - tests/units/test_channel_output_webhook.py  (SSRF via IP literal / hostname)

This file focuses on DNS rebinding: an attacker's hostname resolves to a
public IP on the first request (bypassing naive allow-list checks), then
flips to a private IP on subsequent requests.  advocate validates the
resolved address on every call, so the rebind is caught.
"""

from __future__ import annotations

import socket
from unittest.mock import patch

from twisted.logger import capturedLogs

from canarytokens.canarydrop import Canarydrop
from canarytokens.channel_dns import ChannelDNS
from canarytokens.channel_output_webhook import WebhookOutputChannel
from canarytokens.models import TokenTypes
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken


REBINDING_HOST = "rebind.attacker.example"


def _make_rebinding_getaddrinfo(port: int):
    """
    Returns a patched getaddrinfo that resolves REBINDING_HOST to 8.8.8.8 on
    the first call and 127.0.0.1 on every subsequent call — simulating a
    DNS rebinding attack.
    """
    call_counter = [0]
    original = socket.getaddrinfo
    ips = ["8.8.8.8", "127.0.0.1"]

    def patched(host, p, *args, **kwargs):
        if host == REBINDING_HOST:
            ip = ips[min(call_counter[0], len(ips) - 1)]
            call_counter[0] += 1
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, p or 80))]
        return original(host, p, *args, **kwargs)

    return patched


def _make_channel(settings: SwitchboardSettings, frontend_settings: FrontendSettings):
    switchboard = Switchboard(settings)
    switchboard.switchboard_settings = settings
    return (
        switchboard,
        WebhookOutputChannel(
            switchboard=switchboard,
            switchboard_scheme=settings.SWITCHBOARD_SCHEME,
            frontend_domain="test.com",
        ),
        ChannelDNS(
            switchboard=switchboard,
            frontend_settings=frontend_settings,
            switchboard_hostname="test.com",
            switchboard_scheme=settings.SWITCHBOARD_SCHEME,
        ),
    )


def _make_drop_and_hit(webhook_url: str):
    cd = Canarydrop(
        type=TokenTypes.DNS,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=True,
        alert_webhook_url=webhook_url,
        canarytoken=Canarytoken(),
        memo="dns-rebinding test",
        browser_scanner_enabled=False,
    )
    token_hit = Canarytoken.create_token_hit(
        token_type=TokenTypes.DNS,
        input_channel="not_valid",
        src_ip="1.2.3.4",
        hit_info={"some": "data"},
    )
    cd.add_canarydrop_hit(token_hit=token_hit)
    return cd, token_hit


# ---------------------------------------------------------------------------
# DNS rebinding
# ---------------------------------------------------------------------------


def test_dns_rebinding_round1_allowed_round2_blocked(
    setup_db,
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
):
    """
    Round 1: REBINDING_HOST resolves to 8.8.8.8 (public) — advocate allows
    the attempt; the connection fails with ConnectionError (no server there).

    Round 2: DNS flips to 127.0.0.1 — advocate detects the private address
    and logs "Disallowed requests to", proving the rebind is blocked.
    """
    port = 9999  # no server running here; round 1 will ConnectionError
    url = f"http://{REBINDING_HOST}:{port}/"

    _, webhook_channel, input_channel = _make_channel(settings, frontend_settings)

    with patch("socket.getaddrinfo", side_effect=_make_rebinding_getaddrinfo(port)):
        # Round 1 — public IP, no server → ConnectionError → returns False
        cd, token_hit = _make_drop_and_hit(url)
        with capturedLogs() as captured_r1:
            webhook_channel.send_alert(
                canarydrop=cd,
                token_hit=token_hit,
                input_channel=input_channel,
            )
        assert any(
            "Failed connecting to webhook" in log["log_format"] for log in captured_r1
        ), "Round 1 should fail with a connection error (no server at 8.8.8.8)"

        # Round 2 — DNS rebind to 127.0.0.1 → advocate blocks it
        cd, token_hit = _make_drop_and_hit(url)
        with capturedLogs() as captured_r2:
            webhook_channel.send_alert(
                canarydrop=cd,
                token_hit=token_hit,
                input_channel=input_channel,
            )
        assert any(
            "Disallowed requests to" in log["log_format"] for log in captured_r2
        ), "Round 2 should be blocked by advocate after DNS rebind to 127.0.0.1"


def test_dns_rebinding_crafted_hostname_blocked(
    setup_db,
    frontend_settings: FrontendSettings,
    settings: SwitchboardSettings,
):
    """
    Attacker controls DNS and points their hostname straight at 127.0.0.1.
    advocate resolves the hostname and rejects the request immediately.
    """
    original_getaddrinfo = socket.getaddrinfo

    def crafted_dns(host, p, *args, **kwargs):
        if host == "evil.attacker-controlled.example":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", p or 80))]
        return original_getaddrinfo(host, p, *args, **kwargs)

    _, webhook_channel, input_channel = _make_channel(settings, frontend_settings)
    cd, token_hit = _make_drop_and_hit("http://evil.attacker-controlled.example:9999/")

    with patch("socket.getaddrinfo", side_effect=crafted_dns):
        with capturedLogs() as captured:
            webhook_channel.send_alert(
                canarydrop=cd,
                token_hit=token_hit,
                input_channel=input_channel,
            )

    assert any(
        "Disallowed requests to" in log["log_format"] for log in captured
    ), "Hostname resolving to 127.0.0.1 should be blocked by advocate"
