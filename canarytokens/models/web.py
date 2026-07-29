from typing import List, Literal, Optional

from pydantic import ConfigDict

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
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB
    request_headers: Optional[dict] = None
    request_args: Optional[dict] = None
    additional_info: AdditionalInfo = AdditionalInfo()


class WebBugTokenHistory(TokenHistory[WebBugTokenHit]):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB
    hits: List[WebBugTokenHit] = []
