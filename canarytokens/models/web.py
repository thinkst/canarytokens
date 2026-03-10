from typing import List, Literal, Optional
from .common import (
    AdditionalInfo,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class WebBugTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB


class WebBugTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB


class WebBugTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB
    request_headers: Optional[dict]
    request_args: Optional[dict]
    additional_info: AdditionalInfo = AdditionalInfo()

    class Config:
        allow_population_by_field_name = True


class WebBugTokenHistory(TokenHistory[WebBugTokenHit]):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB
    hits: List[WebBugTokenHit] = []
