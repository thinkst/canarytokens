from typing import List, Literal
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class DNSTokenRequest(TokenRequest):
    """"""

    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.DNS,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "webhook_url": "https://slack.com/api/api.test",
            },
        }


class DNSTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.DNS,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "webhook_url": "https://slack.com/api/api.test",
            },
        }


class DNSTokenHit(TokenHit):
    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS


class DNSTokenHistory(TokenHistory[DNSTokenHit]):
    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS
    hits: List[DNSTokenHit]
