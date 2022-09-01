import re
import zlib

import dns
import pytest
from pydantic import HttpUrl

from canarytokens.models import (
    CANARY_PDF_TEMPLATE_OFFSET,
    V2,
    Memo,
    PDFTokenHistory,
    PDFTokenRequest,
    PDFTokenResponse,
)
from tests.utils import (
    create_token,
    download_token_artifact,
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
def test_pdf_token(version, webhook_receiver, runv2, runv3):
    run_or_skip(version, runv2=runv2, runv3=runv3)
    # Generate the token
    token_request = PDFTokenRequest(
        webhook_url=HttpUrl(url=webhook_receiver, scheme="https"),
        memo=Memo("Test stuff break stuff test stuff sometimes build stuff"),
    )
    resp = create_token(token_request, version=version)
    token_info = PDFTokenResponse(**resp)

    # Get the PDF
    contents = download_token_artifact(
        token_info=token_info, version=version, fmt="pdf"
    )

    # Extract the token url from the PDF
    STREAM_OFFSET = CANARY_PDF_TEMPLATE_OFFSET
    stream_size = int(re.findall(rb"\/Length ([0-9]+)\/", contents[STREAM_OFFSET:])[0])
    stream_start = STREAM_OFFSET + contents[STREAM_OFFSET:].index(b"stream\r\n") + 8
    stream = contents[stream_start : stream_start + stream_size]  # noqa: E203
    raw_stream = zlib.decompress(stream)
    token_url = re.findall(rb"URI\(([^\)]+)\)", raw_stream)[0].decode("utf-8")
    token_domain_name = token_url.split("/")[2]
    if isinstance(version, V2):
        # v2 gives incorrect hostname as it should be NXDOMAIN as it's a PDF.
        token_info.hostname = token_domain_name
    assert token_domain_name == token_info.hostname
    # Trigger the token by direct DNS
    from tests.utils import plain_fire_token

    with pytest.raises(dns.resolver.NXDOMAIN):
        # we expect a NXDOMAIN response
        # Don't want retries
        plain_fire_token.__wrapped__(token_info, version=version)

    # Check it was triggered  at least once (requests.get retries sometimes)
    history_resp = get_token_history(token_info, version=version)
    token_history = PDFTokenHistory(**history_resp)
    ()

    assert len(token_history.hits) >= 1
