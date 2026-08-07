from typing import List, Literal, Optional, TypedDict
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


class CSSClonedSite(TypedDict):
    expected_referrer: str


class CSSClonedWebTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    expected_referrer: str


class CSSClonedWebTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    css: Optional[str] = None
    client_id: Optional[str] = None


class CSSClonedWebTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    referrer: Optional[str] = None
    tls_ja4_fingerprint: Optional[str] = None


class CSSClonedWebTokenHistory(TokenHistory[CSSClonedWebTokenHit]):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    hits: List[CSSClonedWebTokenHit] = []


class DownloadCSSClonedWebRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.CSSCLONEDSITE] = DownloadFmtTypes.CSSCLONEDSITE


class DownloadCSSClonedWebResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str
