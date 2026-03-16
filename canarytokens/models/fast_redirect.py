from typing import List, Literal, Optional, Union
from .common import (
    AdditionalInfo,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class FastRedirectTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT
    redirect_url: str

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.FAST_REDIRECT,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "redirect_url": "https://youtube.com",
            },
        }


class FastRedirectTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.DNS,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "webhook_url": "https://slack.com/api/api.test",
            },
        }


class FastRedirectTokenHit(TokenHit):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT
    referer: Optional[Union[str, bytes]]
    location: Optional[Union[str, bytes]]
    additional_info: AdditionalInfo = AdditionalInfo()


class FastRedirectTokenHistory(TokenHistory[FastRedirectTokenHit]):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT
    hits: List[FastRedirectTokenHit]
