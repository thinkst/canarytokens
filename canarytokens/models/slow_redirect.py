from typing import List, Literal, Optional, Union
from .common import (
    AdditionalInfo,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class SlowRedirectTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SLOW_REDIRECT] = TokenTypes.SLOW_REDIRECT
    # TODO: tighten this up so redirects are validated
    # https://github.com/thinkst/canarytokens/issues/122
    redirect_url: str

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.SLOW_REDIRECT,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "redirect_url": "https://youtube.com",
            },
        }


class SlowRedirectTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SLOW_REDIRECT] = TokenTypes.SLOW_REDIRECT


class SlowRedirectTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SLOW_REDIRECT] = TokenTypes.SLOW_REDIRECT
    referer: Optional[Union[str, bytes]]
    location: Optional[Union[str, bytes]]
    additional_info: AdditionalInfo = AdditionalInfo()


class SlowRedirectTokenHistory(TokenHistory[SlowRedirectTokenHit]):
    token_type: Literal[TokenTypes.SLOW_REDIRECT] = TokenTypes.SLOW_REDIRECT
    hits: List[SlowRedirectTokenHit]
