from enum import Enum
from typing import List, Literal, Optional, Union
from .common import (
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
    DownloadContentTypes,
    DownloadFmtTypes,
    TokenDownloadRequest,
    TokenDownloadResponse,
)


class McpAlertOn(Enum):
    connect = "connect"
    tool_call = "tool_call"


class McpTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.MCP] = TokenTypes.MCP
    mcp_alert_on: McpAlertOn
    gen_aws: Optional[bool] = False


class McpTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.MCP] = TokenTypes.MCP
    mcpjson: Optional[str]


class McpTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MCP] = TokenTypes.MCP
    tool_called: Optional[Union[str, bytes]]


class McpTokenHistory(TokenHistory[McpTokenHit]):
    token_type: Literal[TokenTypes.MCP] = TokenTypes.MCP
    hits: List[McpTokenHit] = []


class DownloadMcpRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.MCP] = DownloadFmtTypes.MCP


class DownloadMcpResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str
