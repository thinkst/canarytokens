from io import BytesIO
from tempfile import SpooledTemporaryFile
from typing import List, Literal
from pydantic import ConfigDict, BaseModel, field_validator
from .common import (
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class UploadedExe(BaseModel):
    content_type: Literal["application/x-msdownload", "application/octet-stream"]
    filename: str
    file: SpooledTemporaryFile
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        schema["title"] = "File"
        return schema


class CustomBinaryTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    signed_exe: UploadedExe
    model_config = ConfigDict(arbitrary_types_allowed=True)


class CustomBinaryTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    file_name: str
    file_contents: str
    hostname: str  # Hostname Local testing fails this check on NXDOMAIN TODO: FIXME

    @field_validator("file_contents", mode="before")
    @classmethod
    def check_file_contents(cls, file_contents: str) -> str:
        if not file_contents.startswith("data:octet/stream;base64"):
            raise ValueError("File contents must be base64 encoded")
        return file_contents


class CustomBinaryTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE


class CustomBinaryTokenHistory(TokenHistory[CustomBinaryTokenHit]):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    hits: List[CustomBinaryTokenHit] = []
