from typing import List, Literal

from pydantic import validator
from .common import (
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


class CMDTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CMD] = TokenTypes.CMD
    cmd_process: str

    @validator("cmd_process")
    def check_process_name(value: str):
        if not value.endswith(".exe"):
            raise ValueError(f"cmd_process must end in .exe. Given: {value}")
        return value


class CMDTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CMD] = TokenTypes.CMD
    reg_file: str


class CMDTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CMD] = TokenTypes.CMD


class CMDTokenHistory(TokenHistory[CMDTokenHit]):
    token_type: Literal[TokenTypes.CMD] = TokenTypes.CMD
    hits: List[CMDTokenHit]


class DownloadCMDRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.CMD] = DownloadFmtTypes.CMD


class DownloadCMDResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str
