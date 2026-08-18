from ipaddress import IPv4Address
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, EmailStr, field_serializer, validator
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


class SMTPMailField(BaseModel):
    sender: Optional[str] = None
    recipients: list[str]
    links: list[str]
    headers: list[str]
    helo: SMTPHeloField
    attachments: list[str]

    @field_serializer("recipients")
    def serialize_recipients(self, recipients: list[str]) -> list[str]:
        return [f"<{recipient}>" for recipient in recipients]


class SMTPTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP


class SMTPTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    unique_email: Optional[EmailStr] = None

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
    mail: Optional[SMTPMailField] = None


class SMTPTokenHistory(TokenHistory[SMTPTokenHit]):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    hits: List[SMTPTokenHit] = []
