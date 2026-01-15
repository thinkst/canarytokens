import os
import re
import tempfile
from io import BytesIO
from zipfile import ZipFile

import pytest
import requests

from canarytokens.models import (
    Memo,
    TokenTypes,
    WindowsDirectoryTokenHistory,
    WindowsDirectoryTokenRequest,
    WindowsDirectoryTokenResponse,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric
from canarytokens.utils import strtobool

from tests.utils import (
    create_token,
    get_stats_from_webhook,
    get_token_history,
    v3,
    windows_directory_fire_token,
)

MODE_DIRECTORY = 0x10


@pytest.mark.parametrize(
    "test_user,test_computer,test_domain",
    [
        ("uSeRnaME1", "cOMp-1", "teSTdoMAin"),
    ],
)
@pytest.mark.parametrize(
    "version",
    [
        v3,
    ],
)
def test_windows_directory(
    test_user: str,
    test_computer: str,
    test_domain: str,
    tmpdir,
    version,
    webhook_receiver,
):

    # initialize request
    memo = "windows directory memo!"
    token_request = WindowsDirectoryTokenRequest(
        token_type=TokenTypes.WINDOWS_DIR, webhook_url=webhook_receiver, memo=Memo(memo)
    )

    # Create windows folder token
    resp = create_token(token_request=token_request, version=version)
    token_info = WindowsDirectoryTokenResponse(**resp)

    # request and download generated widows folder zip
    fmt = "zip"
    windows_folder_request_params = {
        "token": token_info.token,
        "auth": token_info.auth_token,
        "fmt": fmt,
    }
    download_resp = requests.get(
        url=f"{version.server_url}/download",
        params=windows_folder_request_params,
    )

    # Extract windows folder document
    windows_folder_zip_name = (
        download_resp.headers["Content-Disposition"].split(" ")[1].split("=")[1]
    )
    windows_folder_zip_bytes = download_resp.content

    # create temp directory and file
    tmpdir = tempfile.mkdtemp()
    windows_folder_zip_file = "{tmpdir}/{file}".format(
        tmpdir=tmpdir, file=windows_folder_zip_name
    )
    with open(windows_folder_zip_file, "wb") as f:
        f.write(windows_folder_zip_bytes)

    # check file not empty
    assert len(windows_folder_zip_bytes) > 0

    # read windows zip file bytes
    with open(windows_folder_zip_file, "rb") as f:
        input_buf = BytesIO(f.read())

    # extract token url from file
    extracted_url = ""
    with ZipFile(input_buf, "r") as zipfile:
        for zipinfo in zipfile.filelist:
            if zipinfo.external_attr & MODE_DIRECTORY:
                continue
            dirname = tempfile.mkdtemp()
            fname = zipfile.extract(zipinfo, dirname)
            with open(fname, "rb") as fd:
                contents = fd.read()
                icon_resource_text = contents.decode("utf-16").strip().split("\r\n")[1]
                icon_resource_url = re.search(
                    r"IconResource=\\\\(.+?)$", icon_resource_text
                ).group(1)
                extracted_url = (
                    icon_resource_url.replace("\\", "/")
                    .replace("%USERNAME%", test_user)
                    .replace("%COMPUTERNAME%", test_computer)
                    .replace("%USERDOMAIN%", test_domain)
                )

    # validate token url
    assert extracted_url
    assert extracted_url.split(".INI.")[1].startswith(token_info.hostname)
    assert extracted_url.split(".INI.")[0]

    # trigger token
    if strtobool(os.getenv("LIVE", "False")):
        _ = requests.get("{scheme}://{url}".format(scheme="http", url=extracted_url))
    else:
        target_domain = extracted_url.split("/")[0]
        _ = windows_directory_fire_token(token_info, target_domain, version)

    # Check that the returned history has a single hit
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) >= 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    resp = get_token_history(token_info=token_info, version=version)
    token_history = WindowsDirectoryTokenHistory(**resp)
    assert len(token_history.hits) >= 1
    token_hit = token_history.hits[-1]
    assert token_hit.input_channel == "DNS"
    assert token_hit.src_data == {
        "windows_desktopini_access_domain": test_domain.lower(),
        "windows_desktopini_access_hostname": test_computer.lower(),
        "windows_desktopini_access_username": test_user.lower(),
    }
