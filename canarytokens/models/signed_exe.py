from typing import Any, List, Literal
from .common import (
    BaseModel,
    BytesIO,
    SpooledTemporaryFile,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
    validator,
)


class UploadedExe(BaseModel):
    content_type: Literal["application/x-msdownload", "application/octet-stream"]
    filename: str
    file: SpooledTemporaryFile

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

    @classmethod
    def __modify_schema__(cls, field_schema, field):
        field_schema["title"] = "File"


class CustomBinaryTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    signed_exe: UploadedExe

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            SpooledTemporaryFile: lambda v: v.__dict__,
            BytesIO: lambda v: v.__dict__,
        }


class CustomBinaryTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    file_name: str
    file_contents: str
    hostname: str  # Hostname Local testing fails this check on NXDOMAIN TODO: FIXME

    @validator("file_contents", pre=True)
    def check_file_contents(cls, file_contents: str, values: dict[str, Any]) -> str:
        if not file_contents.startswith("data:octet/stream;base64"):
            raise ValueError("File contents must be base64 encoded")
        return file_contents


class CustomBinaryTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE


class CustomBinaryTokenHistory(TokenHistory[CustomBinaryTokenHit]):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    hits: List[CustomBinaryTokenHit] = []
