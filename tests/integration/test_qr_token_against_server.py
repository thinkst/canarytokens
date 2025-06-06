import base64
import io

import pytest
import requests
from PIL import Image
from pyzbar.pyzbar import decode

from canarytokens.models import (
    Memo,
    QRCodeTokenHistory,
    QRCodeTokenRequest,
    QRCodeTokenResponse,
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


@pytest.mark.parametrize(
    "version",
    [
        v2,
        v3,
    ],
)
def test_qr_code_token(version, webhook_receiver, runv2, runv3):
    run_or_skip(version, runv2=runv2, runv3=runv3)
    memo = "qr code memo!"
    token_request = QRCodeTokenRequest(
        token_type=TokenTypes.QR_CODE,
        webhook_url=webhook_receiver,
        memo=Memo(memo),
    )
    # Create QRCode token
    resp = create_token(token_request=token_request, version=version)
    token_info = QRCodeTokenResponse(**resp)

    # Validate token
    image_bytes = io.BytesIO(
        base64.b64decode(token_info.qrcode_png.split(",", maxsplit=1)[1].encode())
    )

    qr_code = Image.open(image_bytes)
    # qr code size is variable
    # assert qr_code.size == (285, 285)
    assert qr_code.mode == "1"

    info = decode(qr_code)[0]
    assert info.type == "QRCODE"
    assert info.orientation == "UP"
    assert info.data.decode() == str(token_info.token_url)

    # Check token url page extension
    assert not token_info.token_url.lower().endswith((".png", ".gif", ".jpg"))

    # Trigger token
    trigger_http_token(
        token_info=token_info,
        version=version,
    )

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])
    resp = get_token_history(token_info=token_info, version=version)
    token_history = QRCodeTokenHistory(**resp)
    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "HTTP"
    if version.live:
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    else:
        assert token_hit.geo_info.ip == "127.0.0.1"
