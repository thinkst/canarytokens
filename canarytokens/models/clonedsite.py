from typing import List, Literal, Optional, Union
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class ClonedWebTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    clonedsite: str


class ClonedWebTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    clonedsite_js: Optional[str] = None


class ClonedWebTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    # TODO fix API spelling to 'referrer' (comes from JS document.referrer)
    referer: Optional[Union[str, bytes]] = None
    location: Optional[Union[str, bytes]] = None


class ClonedWebTokenHistory(TokenHistory[ClonedWebTokenHit]):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    hits: List[ClonedWebTokenHit] = []
