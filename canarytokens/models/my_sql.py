from typing import List, Literal, Optional
from .common import (
    AdditionalInfo,
    DownloadContentTypes,
    DownloadFmtTypes,
    TokenDownloadRequest,
    TokenDownloadResponse,
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


class DownloadMySQLRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.MYSQL] = DownloadFmtTypes.MYSQL
    encoded: bool = True


class DownloadMySQLResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.APPZIP] = DownloadContentTypes.APPZIP
    filename: str
    token: str
    auth: str
