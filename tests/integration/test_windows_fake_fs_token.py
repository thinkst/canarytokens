import random
import pytest

from canarytokens.models import (
    WindowsFakeFSTokenHistory,
    WindowsFakeFSTokenRequest,
    WindowsFakeFSTokenResponse,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric

from tests.utils import (
    clear_stats_on_webhook,
    trigger_windows_fake_fs_token,
    create_token,
    get_stats_from_webhook,
    get_token_history,
    run_or_skip,
    v3,
)


@pytest.mark.parametrize("version", [v3])
@pytest.mark.parametrize(
    "file_name, process_name",
    [
        ("doc b.docx", "explorer.exe"),
        ("doc b.doc", "explorer.exe"),
    ],
)
def test_windows_fake_fs_token_fires(
    file_name: str,
    process_name: str,
    webhook_receiver,
    version,
    runv2,
    runv3,
):
    """
    Tests the Windows Fake FS token.
    """
    run_or_skip(version, runv2=runv2, runv3=runv3)
    expected_hits = 1

    # Create a Windows Fake File System token request
    memo = "Test stuff break stuff test stuff sometimes build stuff"
    root_dir = r"C:\Secrets"
    file_structure = "TESTFS"

    token_request = WindowsFakeFSTokenRequest(
        webhook_url=webhook_receiver,
        memo=memo,
        windows_fake_fs_root=root_dir,
        windows_fake_fs_file_structure=file_structure,
    )
    resp = create_token(token_request, version=version)

    # Check dns token has correct attributes
    token_info = WindowsFakeFSTokenResponse(**resp)
    assert token_info.token in token_info.hostname.split(".")

    clear_stats_on_webhook(webhook_receiver, token=token_info.token)
    # Trigger token twice, make sure the invocation ID limits it to one hit
    invocation_id = random.randint(1000, 10000)
    _ = trigger_windows_fake_fs_token(
        token_info=token_info,
        version=version,
        invocation_id=invocation_id,
        file_name=file_name,
        process_name=process_name,
    )
    _ = trigger_windows_fake_fs_token(
        token_info=token_info,
        version=version,
        invocation_id=invocation_id,
        file_name=file_name,
        process_name=process_name,
    )

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats is not None:
        # Check that what was sent to the webhook is consistent.
        assert len(stats) == expected_hits
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    # Check that the returned history has a single hit.
    resp = get_token_history(token_info=token_info, version=version)

    token_history = WindowsFakeFSTokenHistory(**resp)
    assert len(token_history.hits) == expected_hits
