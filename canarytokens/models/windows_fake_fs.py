import re
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


class WindowsFakeFSTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WINDOWS_FAKE_FS] = TokenTypes.WINDOWS_FAKE_FS
    windows_fake_fs_root: str
    windows_fake_fs_file_structure: str

    @validator("windows_fake_fs_root")
    def check_process_name(value: str):
        _value = value.strip()
        invalid_chars = r'[<>:"/|?*[\]]'
        drive_pattern = r"^[A-Za-z]:[\\/]"

        if not re.match(drive_pattern, _value):
            raise ValueError(
                f"windows_fake_fs_root does not have a drive letter specified. Given: {_value}"
            )
        folder_path = re.sub(drive_pattern, "", _value, 1)
        if re.search(invalid_chars, folder_path):
            raise ValueError(
                f"windows_fake_fs_root contains invalid Windows Path Characters. Given: {_value}"
            )
        if _value.endswith("."):
            raise ValueError(
                f"windows_fake_fs_root cannot end with a fullstop. Given: {_value}"
            )

        return _value


class WindowsFakeFSTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WINDOWS_FAKE_FS] = TokenTypes.WINDOWS_FAKE_FS
    powershell_file: str


class WindowsFakeFSTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WINDOWS_FAKE_FS] = TokenTypes.WINDOWS_FAKE_FS


class WindowsFakeFSTokenHistory(TokenHistory[WindowsFakeFSTokenHit]):
    token_type: Literal[TokenTypes.WINDOWS_FAKE_FS] = TokenTypes.WINDOWS_FAKE_FS
    hits: List[WindowsFakeFSTokenHit]


class DownloadWindowsFakeFSRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.WINDOWS_FAKE_FS] = DownloadFmtTypes.WINDOWS_FAKE_FS


class DownloadWindowsFakeFSResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str
