import re
import tempfile
from io import BytesIO
from zipfile import ZipFile

import pytest
import requests

from canarytokens.models import (
    Memo,
    MsExcelDocumentTokenHistory,
    MsExcelDocumentTokenRequest,
    MsExcelDocumentTokenResponse,
    TokenTypes,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric
from tests.utils import (
    create_token,
    get_stats_from_webhook,
    get_token_history,
    run_or_skip,
    trigger_http_token,
    v2,
    v3,
)

MODE_DIRECTORY = 0x10


@pytest.mark.parametrize(
    "version",
    [
        v2,
        v3,
    ],
)
def test_microsoft_excel_document(tmpdir, version, webhook_receiver, runv2, runv3):
    run_or_skip(version, runv2=runv2, runv3=runv3)
    # initialize request
    memo = "microsoft excel memo!"
    token_request = MsExcelDocumentTokenRequest(
        token_type=TokenTypes.MS_EXCEL, webhook_url=webhook_receiver, memo=Memo(memo)
    )

    # Create microsoft word token
    resp = create_token(token_request=token_request, version=version)
    token_info = MsExcelDocumentTokenResponse(**resp)

    # request and download generated excel document
    fmt = "msexcel"
    word_document_request_params = {
        "token": token_info.token,
        "auth": token_info.auth_token,
        "fmt": fmt,
    }
    download_resp = requests.get(
        url=f"{version.server_url}/download",
        params=word_document_request_params,
    )

    # Extract microsoft word document
    microsoft_excel_doc_name = (
        download_resp.headers["Content-Disposition"].split(" ")[1].split("=")[1]
    )
    microsoft_excel_doc_bytes = download_resp.content

    # create temp directory and  file
    tmpdir = tempfile.mkdtemp()
    excel_file = "{tmpdir}/{file}".format(tmpdir=tmpdir, file=microsoft_excel_doc_name)
    with open(excel_file, "wb") as f:
        f.write(microsoft_excel_doc_bytes)

    # check file not empty
    assert len(microsoft_excel_doc_bytes) > 0

    # read ms excel file byte
    with open(excel_file, "rb") as f:
        input_buf = BytesIO(f.read())

    # extract token url from file
    extracted_url = ""
    with ZipFile(input_buf, "r") as zipfile:
        for zipinfo in zipfile.filelist:
            if zipinfo.external_attr & MODE_DIRECTORY:
                continue

            dirname = tempfile.mkdtemp()
            fname = zipfile.extract(zipinfo, dirname)
            with open(fname, "r") as fd:
                contents = fd.read()
                if "image" in contents:
                    extracted_url = re.search('Target="(.+?)" ', contents).group(1)

    # validate token url
    assert extracted_url
    assert extracted_url == token_info.token_url

    # Check token url page extension
    assert not token_info.token_url.lower().endswith((".png", ".gif", ".jpg", ".jpeg"))

    # trigger token
    resp = trigger_http_token(token_info=token_info, version=version)

    # Check that the returned history has a single hit
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    resp = get_token_history(token_info=token_info, version=version)
    token_history = MsExcelDocumentTokenHistory(**resp)
    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "HTTP"
