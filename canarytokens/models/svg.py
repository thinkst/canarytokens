from typing import List, Literal, Optional

from pydantic import ConfigDict

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
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    token_type: Literal[TokenTypes.SVG] = TokenTypes.SVG
    request_headers: Optional[dict] = None
    request_args: Optional[dict] = None
    additional_info: AdditionalInfo = AdditionalInfo()


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
