from typing import List, Literal, TypedDict

from .common import (
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class OnePassword(TypedDict):
    email_addr: str


class OnePasswordTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.ONE_PASSWORD] = TokenTypes.ONE_PASSWORD
    username: str


class OnePasswordTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.ONE_PASSWORD] = TokenTypes.ONE_PASSWORD
    email_addr: str


class OnePasswordTokenHit(TokenHit):
    token_type: Literal[TokenTypes.ONE_PASSWORD] = TokenTypes.ONE_PASSWORD


class OnePasswordTokenHistory(TokenHistory):
    token_type: Literal[TokenTypes.ONE_PASSWORD] = TokenTypes.ONE_PASSWORD
    hits: List[OnePasswordTokenHit] = []
