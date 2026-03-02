"""
SSRF and DNS-rebinding protection audit — our advocate configuration.

Purpose
-------
These tests verify that the AddrValidator configuration canarytokens uses
for all outbound HTTP requests (WEBHOOK_ADDR_VALIDATOR) correctly blocks
SSRF and DNS-rebinding attacks.

They import WEBHOOK_ADDR_VALIDATOR directly from production code so that
any accidental relaxation of the validator config (e.g. adding an IP
whitelist, enabling internal addresses) will immediately break these tests.
"""

from __future__ import annotations

import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch

import pytest
import requests as vanilla_requests

import advocate
import advocate.exceptions

from canarytokens.channel_output_webhook import WEBHOOK_ADDR_VALIDATOR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _OKHandler(BaseHTTPRequestHandler):
    """Minimal HTTP server that returns 200 OK for any request."""

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"internal-service-response")

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"internal-service-response")

    def log_message(self, *_):
        pass  # silence test output


def _start_local_server(host: str = "127.0.0.1") -> tuple[HTTPServer, str]:
    server = HTTPServer((host, 0), _OKHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    _, port = server.server_address
    return server, f"http://{host}:{port}/"


def _our_get(url: str, **kwargs):
    """advocate.get using our production validator — matches how we call it."""
    return advocate.get(url, timeout=2, validator=WEBHOOK_ADDR_VALIDATOR, **kwargs)


def _our_post(url: str, **kwargs):
    """advocate.post using our production validator — matches how we call it."""
    return advocate.post(url, timeout=2, validator=WEBHOOK_ADDR_VALIDATOR, **kwargs)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def internal_server():
    """Live HTTP server on loopback, simulating an internal service."""
    server, url = _start_local_server()
    yield url
    server.shutdown()


# ---------------------------------------------------------------------------
# 1. SSRF via IP literal
#
#    Attacker embeds a private IP directly in the URL (e.g. http://127.0.0.1/).
#    No DNS resolution involved.
# ---------------------------------------------------------------------------


class TestSSRFViaIPLiteral:
    """Attacker embeds a private IP address directly in the URL."""

    def test_vanilla_requests_reaches_internal_server(self, internal_server):
        """
        Vanilla requests connects to the loopback address without any checks.
        The response arrives — this is the SSRF attack succeeding.
        """
        response = vanilla_requests.get(internal_server, timeout=2)
        assert response.status_code == 200
        assert b"internal-service-response" in response.content

    def test_our_validator_blocks_ip_literal(self, internal_server):
        """Our WEBHOOK_ADDR_VALIDATOR raises before connecting to the private IP."""
        with pytest.raises(advocate.exceptions.UnacceptableAddressException):
            _our_get(internal_server)


@pytest.mark.parametrize(
    "url",
    [
        "http://10.0.0.1/",
        "http://172.16.0.1/",
        "http://192.168.1.1/",
        "http://169.254.169.254/",  # AWS IMDS
        "http://[::1]/",  # IPv6 loopback
        "http://[fc00::1]/",  # IPv6 ULA
    ],
)
def test_our_validator_blocks_all_private_ip_ranges(url):
    """WEBHOOK_ADDR_VALIDATOR rejects every standard private/reserved range."""
    with pytest.raises(advocate.exceptions.UnacceptableAddressException):
        _our_get(url)


# ---------------------------------------------------------------------------
# 2. SSRF via hostname
#
#    The URL looks benign but the hostname resolves to a private IP.
#    Protection must validate *after* DNS resolution.
# ---------------------------------------------------------------------------


class TestSSRFViaHostname:
    """Attacker uses a hostname whose DNS record points to a private IP."""

    def test_vanilla_requests_reaches_localhost(self, internal_server):
        """
        ``localhost`` resolves to 127.0.0.1; vanilla requests follows through
        and the SSRF succeeds.
        """
        port = internal_server.split(":")[-1].rstrip("/")
        url = f"http://localhost:{port}/"
        response = vanilla_requests.get(url, timeout=2)
        assert response.status_code == 200

    def test_our_validator_blocks_localhost(self, internal_server):
        """WEBHOOK_ADDR_VALIDATOR resolves localhost → 127.0.0.1 and rejects it."""
        port = internal_server.split(":")[-1].rstrip("/")
        url = f"http://localhost:{port}/"
        with pytest.raises(advocate.exceptions.UnacceptableAddressException):
            _our_get(url)

    def test_vanilla_requests_follows_crafted_dns(self, internal_server):
        """
        Attacker controls DNS for their hostname and points it at 127.0.0.1.
        Vanilla requests follows the DNS result and reaches the internal service.
        """
        port = int(internal_server.split(":")[-1].rstrip("/"))
        original_getaddrinfo = socket.getaddrinfo

        def crafted_dns(host, p, *args, **kwargs):
            if host == "evil.attacker-controlled.example":
                return [
                    (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", p or 80))
                ]
            return original_getaddrinfo(host, p, *args, **kwargs)

        with patch("socket.getaddrinfo", side_effect=crafted_dns):
            response = vanilla_requests.get(
                f"http://evil.attacker-controlled.example:{port}/",
                timeout=2,
            )
        assert response.status_code == 200

    def test_our_validator_blocks_crafted_dns(self, internal_server):
        """
        Same crafted DNS as above.  WEBHOOK_ADDR_VALIDATOR resolves the
        hostname, sees 127.0.0.1, and raises before opening a socket.
        """
        port = int(internal_server.split(":")[-1].rstrip("/"))
        original_getaddrinfo = socket.getaddrinfo

        def crafted_dns(host, p, *args, **kwargs):
            if host == "evil.attacker-controlled.example":
                return [
                    (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", p or 80))
                ]
            return original_getaddrinfo(host, p, *args, **kwargs)

        with patch("socket.getaddrinfo", side_effect=crafted_dns):
            with pytest.raises(advocate.exceptions.UnacceptableAddressException):
                _our_get(f"http://evil.attacker-controlled.example:{port}/")


# ---------------------------------------------------------------------------
# 3. DNS rebinding
#
#    Round 1: hostname resolves to a public IP  → passes any pre-connection check.
#    Round 2: DNS flips to 127.0.0.1 (TTL = 0) → reaches the internal service.
# ---------------------------------------------------------------------------


class TestDNSRebinding:
    """
    DNS rebinding: the DNS record for a hostname changes between requests.
    - Request 1: resolves to 8.8.8.8  (public — no alert).
    - Request 2: resolves to 127.0.0.1 (rebind — the attack payload).
    """

    REBINDING_HOST = "rebind.attacker.example"

    def _make_rebinding_getaddrinfo(self, port: int):
        call_counter = [0]
        original = socket.getaddrinfo
        ips = ["8.8.8.8", "127.0.0.1"]

        def rebinding_dns(host, p, *args, **kwargs):
            if host == self.REBINDING_HOST:
                ip = ips[min(call_counter[0], len(ips) - 1)]
                call_counter[0] += 1
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, p or 80))]
            return original(host, p, *args, **kwargs)

        return rebinding_dns, call_counter

    def test_vanilla_requests_falls_for_rebinding(self, internal_server):
        """
        Vanilla requests has no IP validation on any request.
        - Round 1: resolves to 8.8.8.8 — connection refused (no server there).
        - Round 2: DNS flipped to 127.0.0.1 — succeeds (SSRF via rebinding).
        """
        port = int(internal_server.split(":")[-1].rstrip("/"))
        url = f"http://{self.REBINDING_HOST}:{port}/"
        rebinding_dns, _ = self._make_rebinding_getaddrinfo(port)

        with patch("socket.getaddrinfo", side_effect=rebinding_dns):
            with pytest.raises(vanilla_requests.exceptions.ConnectionError):
                vanilla_requests.get(url, timeout=2)

            response = vanilla_requests.get(url, timeout=2)
            assert response.status_code == 200
            assert b"internal-service-response" in response.content

    def test_our_validator_blocks_rebinding(self, internal_server):
        """
        WEBHOOK_ADDR_VALIDATOR validates the resolved IP on *every* request.
        Round 2 (127.0.0.1) is caught and rejected.
        """
        port = int(internal_server.split(":")[-1].rstrip("/"))
        url = f"http://{self.REBINDING_HOST}:{port}/"
        rebinding_dns, _ = self._make_rebinding_getaddrinfo(port)

        with patch("socket.getaddrinfo", side_effect=rebinding_dns):
            # Round 1: 8.8.8.8 — validation passes but connection fails (no server).
            with pytest.raises(
                (
                    advocate.exceptions.UnacceptableAddressException,
                    vanilla_requests.exceptions.ConnectionError,
                )
            ):
                _our_post(url)

            # Round 2: DNS flipped to 127.0.0.1 — our validator raises.
            with pytest.raises(advocate.exceptions.UnacceptableAddressException):
                _our_post(url)
