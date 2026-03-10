from typing import List, Literal, Optional
from .common import (
    AdditionalInfo,
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


class SVGTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SVG] = TokenTypes.SVG


class SVGTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SVG] = TokenTypes.SVG
    svg: str


class SVGTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SVG] = TokenTypes.SVG
    request_headers: Optional[dict]
    request_args: Optional[dict]
    additional_info: AdditionalInfo = AdditionalInfo()

    class Config:
        allow_population_by_field_name = True


class SVGTokenHistory(TokenHistory[SVGTokenHit]):
    token_type: Literal[TokenTypes.SVG] = TokenTypes.SVG
    hits: List[SVGTokenHit]


class DownloadSVGRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.SVG] = DownloadFmtTypes.SVG


class DownloadSVGResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.SVG] = DownloadContentTypes.SVG
    filename: str
    token: str
    auth: str
