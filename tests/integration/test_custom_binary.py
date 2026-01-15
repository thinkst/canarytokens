import base64
import re
import subprocess
import tempfile
import os
import dns
import dns.resolver
import pytest


from canarytokens.models import (
    CustomBinaryTokenHistory,
    CustomBinaryTokenRequest,
    CustomBinaryTokenResponse,
    Memo,
    TokenTypes,
    UploadedExe,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric
from tests.utils import (
    create_token,
    get_stats_from_webhook,
    get_token_history,
    plain_fire_token,
)


@pytest.mark.skipif(os.name == "nt", reason="Skip if nt os (Windows OS)")
@pytest.mark.parametrize(
    "file_name,file_mimetype",
    [
        ("helloWorld.exe", "application/x-msdownload"),
        ("helloWorld.dll", "application/octet-stream"),
    ],
)
def test_custom_binary_token_fire(tmpdir, file_name, file_mimetype, webhook_receiver):

    with open("data/{file}".format(file=file_name), "rb") as fp:
        # record contents
        input_file_contents = fp.read()
        # create SpooledTemporaryFile
        temp_file = tempfile.SpooledTemporaryFile()
        temp_file.write(input_file_contents)
        temp_file.seek(0)

        # initialize request
        signed_exe = UploadedExe(
            filename=file_name, content_type=file_mimetype, file=temp_file
        )
        memo = "signed exe memo!"
        token_request = CustomBinaryTokenRequest(
            signed_exe=signed_exe,
            webhook_url=webhook_receiver,
            memo=Memo(memo),
        )

        # Create signed exe token
        resp = create_token(token_request=token_request)
        token_info = CustomBinaryTokenResponse(**resp)

    _, data = token_info.file_contents.split(",")
    signed_binary_as_bytes = base64.b64decode(data)
    signed_binary_as_bytes
    assert (
        re.search(f"http://{token_info.hostname}".encode(), signed_binary_as_bytes)
        is not None
    )
    # fire token
    try:
        plain_fire_token.__wrapped__(token_info)
    except dns.resolver.NXDOMAIN:
        # we expect a NXDOMAIN response
        pass

    # Check that the returned history has a atleast a single hit
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    resp = get_token_history(token_info=token_info)
    token_history = CustomBinaryTokenHistory(**resp)
    assert len(token_history.hits) >= 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "DNS"


@pytest.mark.skipif(os.name != "nt", reason="Requires nt os (Windows OS)")
@pytest.mark.parametrize(
    "file_name,file_mimetype",
    [
        ("helloWorld.exe", "application/x-msdownload"),
        ("helloWorld.dll", "application/octet-stream"),
    ],
)
def test_custom_binary(tmpdir, file_name, file_mimetype, webhook_receiver):

    with open("data\\{file}".format(file=file_name), "rb") as fp:
        # record contents
        input_file_contents = fp.read()
        # create SpooledTemporaryFile
        temp_file = tempfile.SpooledTemporaryFile()
        temp_file.write(input_file_contents)
        temp_file.seek(0)

        # initialize request
        signed_exe = UploadedExe(
            filename=file_name, content_type=file_mimetype, file=temp_file
        )
        memo = "signed exe memo!"
        token_request = CustomBinaryTokenRequest(
            token_type=TokenTypes.SIGNED_EXE,
            signed_exe=signed_exe,
            webhook_url=webhook_receiver,
            memo=Memo(memo),
        )

        # Create signed exe token
        resp = create_token(token_request=token_request)
        token_info = CustomBinaryTokenResponse(**resp)

    # Extract signed exe
    signed_exe_bytes = base64.b64decode(
        token_info.file_contents.split(",", maxsplit=1)[1].encode()
    )

    # create temp dir and file
    tmpdir = tempfile.mkdtemp()
    with open(
        "{tmpdir}\\response_{file}".format(tmpdir=tmpdir, file=file_name), "wb"
    ) as f:
        f.write(signed_exe_bytes)

    # get returned exe's Authenticode signature, and trigger alerts
    subprocess.Popen(
        [
            "powershell",
            "-command",
            "Get-AuthenticodeSignature",
            "{tmpdir}\\response_{file}".format(tmpdir=tmpdir, file=file_name),
        ]
    )

    # compare file names and outputs
    assert file_name == resp["file_name"]

    # Check that the returned history has a atleast a single hit
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    resp = get_token_history(token_info=token_info)
    token_history = CustomBinaryTokenHistory(**resp)
    assert len(token_history.hits) >= 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "DNS"
