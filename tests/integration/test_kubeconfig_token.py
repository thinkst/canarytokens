import base64
import subprocess
import tempfile

import pytest
import requests

from canarytokens.models import (
    KubeconfigTokenHistory,
    KubeconfigTokenRequest,
    KubeconfigTokenResponse,
    Memo,
    TokenAlertDetailGeneric,
    TokenTypes,
)
from tests.utils import (
    create_token,
    get_stats_from_webhook,
    get_token_history,
    run_or_skip,
    v2,
    v3,
)


@pytest.mark.parametrize(
    "version",
    [
        v2,
        v3,
    ],
)
def test_kubeconfig(tmpdir, version, webhook_receiver, runv2, runv3):
    run_or_skip(version=version, runv2=runv2, runv3=runv3)
    # initialize request
    memo = "kubeconfig memo!"
    token_request = KubeconfigTokenRequest(
        token_type=TokenTypes.KUBECONFIG,
        webhook_url=webhook_receiver,
        memo=Memo(memo),
    )

    # Create kubeconfig token
    resp = create_token(token_request=token_request, version=version)
    token_info = KubeconfigTokenResponse(**resp)

    # check kubeconfig response field is not empty
    assert len(token_info.kubeconfig) > 0
    # Extract kubeconfig response field contents
    token_info_kubeconfig_contents = base64.b64decode(token_info.kubeconfig)

    print(token_info_kubeconfig_contents.decode())

    # request and download generated kubeconfig file
    fmt = "kubeconfig"
    kubeconfig_request_params = {
        "token": token_info.token,
        "auth": token_info.auth_token,
        "fmt": fmt,
    }

    download_resp = requests.get(
        url=f"{version.server_url}/download",
        params=kubeconfig_request_params,
    )
    # Extract kubeconfig downloaded file contents
    kubeconfig_file_downloaded_contents = download_resp.content

    # check kubeconfig downloaded file is not empty
    assert len(kubeconfig_file_downloaded_contents) > 0

    # check downloaded file contents are the same as response field contents
    assert token_info_kubeconfig_contents == kubeconfig_file_downloaded_contents

    # # Extract kubeconfig downloaded filename
    kubeconfig_file_name = (
        download_resp.headers["Content-Disposition"].split(" ")[1].split("=")[1]
    )

    # create temp directory and file
    tmpdir = tempfile.mkdtemp()
    kubeconfig_file = "{tmpdir}/{file}".format(tmpdir=tmpdir, file=kubeconfig_file_name)
    with open(kubeconfig_file, "wb") as f:
        f.write(token_info_kubeconfig_contents)

    # trigger token
    get_nodes_output = subprocess.run(
        [
            "kubectl",
            "--insecure-skip-tls-verify",
            "--kubeconfig={kubeconfig}".format(kubeconfig=kubeconfig_file),
            "get",
            "nodes",
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    print("subprocess finished")
    # check return code
    assert get_nodes_output.returncode == 1

    # check std error message
    print(f"\n\n{get_nodes_output.stderr.decode()}\n\n")
    assert (
        get_nodes_output.stderr
        == b"error: You must be logged in to the server (Unauthorized)\n"
    )

    # Check that the returned history has a at least a single hit
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) >= 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    resp = get_token_history(token_info=token_info, version=version)
    token_history = KubeconfigTokenHistory(**resp)
    assert len(token_history.hits) >= 1
    token_hit = token_history.hits[0]
    # Design: Make Channel input name consistent.
    assert token_hit.input_channel == "Kubeconfig"
