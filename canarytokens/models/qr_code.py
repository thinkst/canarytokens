from typing import Literal
from .common import (
    DownloadContentTypes,
    DownloadFmtTypes,
    TokenDownloadRequest,
    TokenDownloadResponse,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class QRCodeTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE


class QRCodeTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE
    qrcode_png: str


class QRCodeTokenHit(TokenHit):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE


class QRCodeTokenHistory(TokenHistory[QRCodeTokenHit]):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE


class DownloadQRCodeRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.QRCODE] = DownloadFmtTypes.QRCODE


class DownloadQRCodeResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.IMAGE] = DownloadContentTypes.IMAGE
    filename: str
    token: str
    auth: str
