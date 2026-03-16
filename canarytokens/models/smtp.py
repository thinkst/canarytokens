from ipaddress import IPv4Address
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, EmailStr, validator
from .common import (
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class SMTPHeloField(BaseModel):
    client_name: str
    client_ip: IPv4Address

    class Config:
        json_encoders = {
            IPv4Address: lambda v: str(v),
        }


class SMTPMailField(BaseModel):
    sender: Optional[str]
    recipients: list[str]
    links: list[str]
    headers: list[str]
    helo: SMTPHeloField
    attachments: list[str]

    def dict(
        self,
        *,
        include: 'Union["AbstractSetIntStr", "MappingIntStrAny"]' = None,  # noqa F821
        exclude: 'Union["AbstractSetIntStr", "MappingIntStrAny"]' = None,  # noqa F821
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":  # noqa F821
        data = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        # V2 Compatible serialization
        data["recipients"] = [f"<{o}>" for o in data["recipients"]]
        return data


class SMTPTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP


class SMTPTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    unique_email: Optional[EmailStr]

    # FIXME: validate all
    @validator("unique_email", pre=True)
    def set_unique_email(
        cls, unique_email: Optional[EmailStr], values: dict[str, Any]
    ) -> EmailStr:
        if unique_email is None:
            # TODO: mapping from hostname to domain should in some common code
            #       if we do this often.
            if "127.0.0.1" in values["hostname"]:
                domain = "localhost.com"
            else:
                domain = ".".join(values["hostname"].split(".")[-2:])
            return EmailStr(f"{values['token']}@{domain}")
        return unique_email


class SMTPTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    mail: Optional[SMTPMailField]


class SMTPTokenHistory(TokenHistory[SMTPTokenHit]):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    hits: List[SMTPTokenHit] = []
