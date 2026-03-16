from typing import List, Literal, Optional

from pydantic import BaseModel, validator
from .common import (
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class WebDavAdditionalInfo(BaseModel):
    file_path: Optional[str]
    useragent: Optional[str]

    def serialize_for_v2(self) -> dict:
        return self.dict()


class WebDavTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WEBDAV] = TokenTypes.WEBDAV
    webdav_fs_type: str

    @validator("webdav_fs_type")
    def check_webdav_fs_type(value: str):
        from canarytokens.webdav import FsType

        if not value.upper() in FsType.__members__.keys():
            raise ValueError(
                f"webdav_fs_type must be in the FsType enum. Given: {value}"
            )
        return value


class WebDavTokenResponse(TokenResponse):
    webdav_fs_type: str
    token_type: Literal[TokenTypes.WEBDAV] = TokenTypes.WEBDAV
    webdav_password: str
    webdav_server: str


class WebDavTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WEBDAV] = TokenTypes.WEBDAV
    additional_info: Optional[WebDavAdditionalInfo]


class WebDavTokenHistory(TokenHistory[WebDavTokenHit]):
    token_type: Literal[TokenTypes.WEBDAV] = TokenTypes.WEBDAV
    hits: List[WebDavTokenHit] = []
