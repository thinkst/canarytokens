from typing import List, Literal, Optional
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class WindowsDirectoryTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR


class WindowsDirectoryTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR


class WindowsDirectoryTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR
    src_data: Optional[dict]


class WindowsDirectoryTokenHistory(TokenHistory[WindowsDirectoryTokenHit]):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR
    hits: List[WindowsDirectoryTokenHit] = []
