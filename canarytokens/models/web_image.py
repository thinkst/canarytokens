from tempfile import SpooledTemporaryFile
from typing import List, Literal

from pydantic import ConfigDict, BaseModel, Field
from .common import (
    AdditionalInfo,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class UploadedImage(BaseModel):
    content_type: Literal["image/png", "image/gif", "image/jpeg"]
    filename: str
    file: SpooledTemporaryFile = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # Pydantic cannot generate JSON schema for SpooledTemporaryFile.
        return {
            "title": "File",
            "type": "object",
            "properties": {
                "content_type": {
                    "enum": ["image/png", "image/gif", "image/jpeg"],
                    "type": "string"
                },
                "filename": {
                    "type": "string"
                },
                "file": {
                    "type": "string",
                    "format": "binary"
                }
            },
            "required": ["content_type", "filename", "file"]
        }


class CustomImageTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    web_image: UploadedImage
    model_config = ConfigDict(arbitrary_types_allowed=True)


class CustomImageTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE


class CustomImageTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    additional_info: AdditionalInfo = AdditionalInfo()


class CustomImageTokenHistory(TokenHistory[CustomImageTokenHit]):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    hits: List[CustomImageTokenHit] = []
