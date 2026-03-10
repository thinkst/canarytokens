from typing import List, Literal
from .common import (
    AdditionalInfo,
    BaseModel,
    BytesIO,
    SpooledTemporaryFile,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class UploadedImage(BaseModel):
    content_type: Literal["image/png", "image/gif", "image/jpeg"]
    filename: str
    file: SpooledTemporaryFile

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

    @classmethod
    def __modify_schema__(cls, field_schema, field):
        field_schema["title"] = "File"


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
