from typing import Literal
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class QRCodeTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE


class QRCodeTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE
    qrcode_png: str


class QRCodeTokenHit(TokenHit):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE


class QRCodeTokenHistory(TokenHistory[QRCodeTokenHit]):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE
