from typing import List, Literal, Optional
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class SQLServerTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER
    sql_server_sql_action: Optional[Literal["INSERT", "DELETE", "UPDATE", "SELECT"]]
    sql_server_table_name: str = "TABLE1"
    sql_server_view_name: str = "VIEW1"
    sql_server_function_name: str = "FUNCTION1"
    sql_server_trigger_name: str = "TRIGGER1"


class SQLServerTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER
    sql_server_sql_action: Optional[Literal["INSERT", "DELETE", "UPDATE", "SELECT"]]
    sql_server_table_name: Optional[str]
    sql_server_view_name: Optional[str]
    sql_server_function_name: Optional[str]
    sql_server_trigger_name: Optional[str]


class SQLServerTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER


class SQLServerTokenHistory(TokenHistory[SQLServerTokenHit]):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER
    hits: List[SQLServerTokenHit]
