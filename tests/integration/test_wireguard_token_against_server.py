import os
import subprocess
from pathlib import Path

import pytest
from pydantic import HttpUrl

from canarytokens.models import (
    Memo,
    WireguardTokenHistory,
    WireguardTokenRequest,
    WireguardTokenResponse,
)
from canarytokens.utils import strtobool

from tests.utils import create_token, get_token_history, v3


@pytest.mark.parametrize("version", [v3])
@pytest.mark.skipif(
    not strtobool(os.getenv("CI", "False")), reason="Only test wireguard token on ci"
)
def test_wireguard_token(version, webhook_receiver):

    token_request = WireguardTokenRequest(
        webhook_url=HttpUrl(url=webhook_receiver, scheme="https"),
        memo=Memo("Test stuff break stuff test stuff sometimes build stuff"),
    )
    resp = create_token(token_request, version=version)
    token_info = WireguardTokenResponse(**resp)
    wg_config = "/tmp/wg0.conf"
    with open(wg_config, "w") as fp:
        fp.write(token_info.wg_conf)
    # Trigger the token
    sp1 = subprocess.run(["sudo", "wg-quick", "up", wg_config], capture_output=True)
    print(sp1)
    sp2 = subprocess.run(["sudo", "wg-quick", "down", wg_config], capture_output=True)
    print(sp2)
    Path(wg_config).unlink(missing_ok=False)
    # Check that the returned history has a single hit
    history_resp = get_token_history(token_info, version=version)
    token_history = WireguardTokenHistory(**history_resp)

    assert len(token_history.hits) == 1
