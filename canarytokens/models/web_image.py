from io import BytesIO
from tempfile import SpooledTemporaryFile
from typing import Any, List, Literal

from pydantic import BaseModel, ConfigDict
from .common import (
    AdditionalInfo,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class UploadedImage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    content_type: Literal["image/png", "image/gif", "image/jpeg"]
    filename: str
    file: Any

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> dict:
        json_schema = handler(core_schema)
        json_schema["title"] = "File"
        return json_schema


class CustomImageTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    web_image: UploadedImage

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            SpooledTemporaryFile: lambda v: v.__dict__,
            BytesIO: lambda v: v.__dict__,
        }


class CustomImageTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE


class CustomImageTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    additional_info: AdditionalInfo = AdditionalInfo()


class CustomImageTokenHistory(TokenHistory[CustomImageTokenHit]):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    hits: List[CustomImageTokenHit] = []
