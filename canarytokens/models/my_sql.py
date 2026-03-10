from typing import List, Literal, Optional
from .common import (
    AdditionalInfo,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class MySQLTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.MY_SQL] = TokenTypes.MY_SQL


class MySQLTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.MY_SQL] = TokenTypes.MY_SQL
    usage: Optional[str]


class MySQLTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MY_SQL] = TokenTypes.MY_SQL
    additional_info: Optional[AdditionalInfo]


class MySQLTokenHistory(TokenHistory[MySQLTokenHit]):
    token_type: Literal[TokenTypes.MY_SQL] = TokenTypes.MY_SQL
    hits: List[MySQLTokenHit]
