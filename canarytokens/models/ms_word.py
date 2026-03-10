from typing import List, Literal
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class MsWordDocumentTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD


class MsWordDocumentTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD


class MsWordDocumentTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD


class MsWordDocumentTokenHistory(TokenHistory[MsWordDocumentTokenHit]):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD
    hits: List[MsWordDocumentTokenHit] = []
