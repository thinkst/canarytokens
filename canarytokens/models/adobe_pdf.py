from typing import List, Literal
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class PDFTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF


class PDFTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF
    hostname: str  # Hostname Local testing fails this check TODO: FIXME


class PDFTokenHit(TokenHit):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF


class PDFTokenHistory(TokenHistory[PDFTokenHit]):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF
    hits: List[PDFTokenHit]
