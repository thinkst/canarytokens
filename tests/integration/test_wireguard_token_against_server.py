import os
import subprocess
from pathlib import Path

import pytest

from canarytokens.models import (
    Memo,
    WireguardTokenHistory,
    WireguardTokenRequest,
    WireguardTokenResponse,
)
from canarytokens.utils import strtobool

from tests.utils import create_token, get_token_history


@pytest.mark.skipif(
    not strtobool(os.getenv("CI", "False")), reason="Only test wireguard token on ci"
)
def test_wireguard_token(webhook_receiver, tmp_path: Path):
    token_request = WireguardTokenRequest(
        webhook_url=webhook_receiver,
        memo=Memo("Test stuff break stuff test stuff sometimes build stuff"),
    )
    resp = create_token(token_request)
    token_info = WireguardTokenResponse(**resp)
    wg_config = tmp_path / "wg0.conf"
    fd = os.open(wg_config, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fp:
        fp.write(token_info.wg_conf)
    up = subprocess.run(
        ["sudo", "wg-quick", "up", str(wg_config)], capture_output=True, text=True
    )
    assert up.returncode == 0, (
        f"wg-quick up failed ({up.returncode})\nstdout: {up.stdout}\nstderr: {up.stderr}"
    )
    try:
        history_resp = get_token_history(token_info)
        token_history = WireguardTokenHistory(**history_resp)
        assert len(token_history.hits) == 1
    finally:
        down = subprocess.run(
            ["sudo", "wg-quick", "down", str(wg_config)], capture_output=True, text=True
        )
        assert down.returncode == 0, (
            f"wg-quick down failed ({down.returncode})\nstdout: {down.stdout}\nstderr: {down.stderr}"
        )
