from typing import List, Literal, Optional
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class CSSClonedWebTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    expected_referrer: str


class CSSClonedWebTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    css: Optional[str]
    client_id: Optional[str]


class CSSClonedWebTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    referrer: Optional[str]


class CSSClonedWebTokenHistory(TokenHistory[CSSClonedWebTokenHit]):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    hits: List[CSSClonedWebTokenHit] = []
