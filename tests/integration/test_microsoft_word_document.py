import tempfile

import requests
from docx import Document

from canarytokens.models import (
    Memo,
    MsWordDocumentTokenHistory,
    MsWordDocumentTokenRequest,
    MsWordDocumentTokenResponse,
    TokenTypes,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric
from tests.utils import (
    create_token,
    get_stats_from_webhook,
    get_token_history,
    trigger_http_token,
    server_config,
)


def test_microsoft_word_document(tmpdir, webhook_receiver):

    # initialize request
    memo = "microsoft word memo!"
    token_request = MsWordDocumentTokenRequest(
        token_type=TokenTypes.MS_WORD,
        webhook_url=webhook_receiver,
        memo=Memo(memo),
    )

    # Create microsoft word token
    resp = create_token(token_request=token_request)
    token_info = MsWordDocumentTokenResponse(**resp)

    # request and download generated word document
    fmt = "msword"
    word_document_request_params = {
        "token": token_info.token,
        "auth": token_info.auth_token,
        "fmt": fmt,
    }
    download_resp = requests.get(
        url=f"{server_config.server_url}/download",
        params=word_document_request_params,
    )

    # Extract microsoft word document
    microsoft_word_doc_name = (
        download_resp.headers["Content-Disposition"].split(" ")[1].split("=")[1]
    )
    microsoft_word_doc_bytes = download_resp.content

    # create temp directory and file
    tmpdir = tempfile.mkdtemp()
    word_doc = "{tmpdir}/{file}".format(tmpdir=tmpdir, file=microsoft_word_doc_name)
    with open(word_doc, "wb") as f:
        f.write(microsoft_word_doc_bytes)

    # Open document
    document = Document(word_doc)
    # extract token url from document
    extracted_url = ""
    for rel in document.part.rels:
        base_rel = document.part.rels[rel].__dict__["_target"]
        if base_rel:
            secondary_rels = base_rel.__dict__["_rels"]
            if secondary_rels and secondary_rels["rId1"]:
                extracted_url = secondary_rels["rId1"].__dict__["_target"]

    # validate extracted url
    assert extracted_url
    assert extracted_url == token_info.token_url

    # trigger token
    resp = trigger_http_token(token_info=token_info)
    # Check that the returned history has a single hit
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    resp = get_token_history(token_info=token_info)
    token_history = MsWordDocumentTokenHistory(**resp)
    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "HTTP"
