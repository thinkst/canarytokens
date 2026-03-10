from typing import List, Literal
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class SvnTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SVN] = TokenTypes.SVN


class SvnTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SVN] = TokenTypes.SVN


class SvnTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SVN] = TokenTypes.SVN


class SvnTokenHistory(TokenHistory[SvnTokenHit]):
    token_type: Literal[TokenTypes.SVN] = TokenTypes.SVN
    hits: List[SvnTokenHit] = []
