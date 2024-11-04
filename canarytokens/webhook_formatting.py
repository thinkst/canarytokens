from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import re
from functools import partial
from datetime import datetime

from pydantic import BaseModel, HttpUrl, parse_obj_as

from canarytokens import constants
from canarytokens.channel import (
    format_as_discord_canaryalert,
    format_as_googlechat_canaryalert,
    format_as_ms_teams_canaryalert,
)
from canarytokens.models import (
    readable_token_type_names,
    Memo,
    TokenTypes,
    TokenAlertDetails,
    TokenExposedDetails,
)
from canarytokens.utils import json_safe_dict, prettify_snake_case


CANARY_LOGO_ROUND_PUBLIC_URL = parse_obj_as(
    HttpUrl,
    constants.CANARY_IMAGE_URL,
)
WEBHOOK_TEST_URL = parse_obj_as(HttpUrl, "http://example.com/test/url/for/webhook")
TOKEN_EXPOSED_DESCRIPTION = "One of your {readable_type} Canarytokens has been found on the internet. A publicly exposed token will provide very low quality alerts. We recommend that you disable and replace this token on private infrastructure."
MAX_INLINE_LENGTH = 40  # Max length of content to share a line with other content


class HexColor(Enum):
    WARNING = "#ed6c02"
    ERROR = "#d32f2f"
    CANARY_GREEN = "#3ad47f"

    @property
    def decimal_value(self):
        return int(self.value_without_hash, 16)

    @property
    def value_without_hash(self):
        return self.value[1:]


class WebhookType(Enum):
    SLACK = "slack"
    GOOGLE_CHAT = "google-chat"
    DISCORD = "discord"
    MS_TEAMS = "ms-teams"
    GENERIC = "generic"


def _match_url_start(url: str, match_str: str) -> bool:
    return url.startswith(match_str)


def _match_url_regex(url: str, match_regex: str) -> bool:
    return bool(re.match(match_regex, url))


_WEBHOOK_URL_MATCH_CRITERIA = {
    WebhookType.SLACK: partial(
        _match_url_start, match_str=constants.WEBHOOK_BASE_URL_SLACK
    ),
    WebhookType.GOOGLE_CHAT: partial(
        _match_url_start, match_str=constants.WEBHOOK_BASE_URL_GOOGLE_CHAT
    ),
    WebhookType.DISCORD: partial(
        _match_url_start, match_str=constants.WEBHOOK_BASE_URL_DISCORD
    ),
    WebhookType.MS_TEAMS: partial(
        _match_url_regex, match_regex=constants.WEBHOOK_BASE_URL_REGEX_MS_TEAMS
    ),
}


def get_webhook_type(url: str) -> WebhookType:
    for webhook_type, match_func in _WEBHOOK_URL_MATCH_CRITERIA.items():
        if match_func(url):
            return webhook_type
    else:
        return WebhookType.GENERIC


def format_details_for_webhook(
    webhook_type: WebhookType, details: Union[TokenAlertDetails, TokenExposedDetails]
):
    if isinstance(details, TokenAlertDetails):
        return _format_alert_details_for_webhook(webhook_type, details)
    else:
        return _format_exposed_details_for_webhook(webhook_type, details)


def _format_alert_details_for_webhook(
    webhook_type: WebhookType, details: TokenAlertDetails
):
    if webhook_type == WebhookType.SLACK:
        return _format_as_slack_canaryalert(details)
    elif webhook_type == WebhookType.GOOGLE_CHAT:
        return format_as_googlechat_canaryalert(details)
    elif webhook_type == WebhookType.DISCORD:
        return format_as_discord_canaryalert(details)
    elif webhook_type == WebhookType.MS_TEAMS:
        return format_as_ms_teams_canaryalert(details)
    elif webhook_type == WebhookType.GENERIC:
        return TokenAlertDetailGeneric(**details.dict())
    else:
        raise NotImplementedError(
            f"_format_alert_details_for_webhook not implemented for webhook type: {webhook_type}"
        )


def _format_exposed_details_for_webhook(
    webhook_type: WebhookType, details: TokenExposedDetails
):
    if webhook_type == WebhookType.SLACK:
        return _format_as_slack_token_exposed(details)
    elif webhook_type == WebhookType.GOOGLE_CHAT:
        raise NotImplementedError(
            f"_format_exposed_details_for_webhook not implemented for webhook type: {webhook_type}"
        )
    elif webhook_type == WebhookType.DISCORD:
        raise NotImplementedError(
            f"_format_exposed_details_for_webhook not implemented for webhook type: {webhook_type}"
        )
    elif webhook_type == WebhookType.MS_TEAMS:
        raise NotImplementedError(
            f"_format_exposed_details_for_webhook not implemented for webhook type: {webhook_type}"
        )
    elif webhook_type == WebhookType.GENERIC:
        return TokenExposedDetailGeneric(**details.dict())
    else:
        raise NotImplementedError(
            f"_format_alert_details_for_webhook not implemented for webhook type: {webhook_type}"
        )


def generate_webhook_test_payload(webhook_type: WebhookType, token_type: TokenTypes):
    if webhook_type == WebhookType.SLACK:
        return TokenAlertDetailsSlack(
            attachments=[
                SlackAttachment(
                    title="Validating new Canarytokens webhook",
                    text="It's working :tada:!",
                    color=HexColor.CANARY_GREEN.value,
                    footer="Canarytokens",
                    footer_icon=CANARY_LOGO_ROUND_PUBLIC_URL,
                    fields=[],
                )
            ]
        )
    elif webhook_type == WebhookType.GOOGLE_CHAT:
        raise NotImplementedError(
            "generate_webhook_test_payload not implemented for GOOGLE_CHAT"
        )
    elif webhook_type == WebhookType.DISCORD:
        raise NotImplementedError(
            "generate_webhook_test_payload not implemented for DISCORD"
        )
    elif webhook_type == WebhookType.MS_TEAMS:
        raise NotImplementedError(
            "generate_webhook_test_payload not implemented for MS_TEAMS"
        )
    elif webhook_type == WebhookType.GENERIC:
        return TokenAlertDetails(
            manage_url=WEBHOOK_TEST_URL,
            channel="HTTP",
            memo=Memo("Congrats! The newly saved webhook works"),
            token="a+test+token",
            token_type=token_type,
            src_ip="127.0.0.1",
            additional_data={
                "src_ip": "1.1.1.1",
                "useragent": "Mozilla/5.0...",
                "referer": "http://example.com/referrer",
                "location": "http://example.com/location",
            },
            time=datetime.now(),
        )
    else:
        raise NotImplementedError(
            f"generate_webhook_test_payload not implemented for {webhook_type}"
        )


def _format_as_slack_canaryalert(details: TokenAlertDetails) -> TokenAlertDetailsSlack:
    """
    Transforms `TokenAlertDetails` to `TokenAlertDetailsSlack`.
    """
    fields: List[SlackField] = [
        SlackField(title="Channel", value=details.channel),
        SlackField(title="Token Reminder", value=details.memo),
        SlackField(
            title="Time",
            value=details.time.strftime("%Y-%m-%d %H:%M:%S (UTC)"),
        ),
    ]

    if details.src_data:
        fields.extend(_data_to_slack_fields(details.src_data))
    if details.additional_data:
        fields.extend(_data_to_slack_fields(details.additional_data))

    fields.append(
        SlackField(title="Manage token", value=details.manage_url, short=False)
    )

    attachments = [
        SlackAttachment(
            title_link=details.manage_url,
            fields=fields,
            footer="Canarytokens",
            footer_icon=CANARY_LOGO_ROUND_PUBLIC_URL,
            ts=details.time.timestamp(),
            color=HexColor.ERROR.value,
        )
    ]
    return TokenAlertDetailsSlack(attachments=attachments)


def _format_as_slack_token_exposed(
    details: TokenExposedDetails,
) -> TokenAlertDetailsSlack:
    fields: List[SlackField] = [
        SlackField(title="Token Reminder", value=details.memo),
        SlackField(title="Key ID", value=details.key_id),
        SlackField(title="Manage token", value=details.manage_url, short=False),
    ]

    if details.public_location:
        fields.insert(
            2,
            SlackField(
                title="Key exposed here", value=details.public_location, short=False
            ),
        )

    attachments = [
        SlackAttachment(
            title="Canarytoken Exposed",
            title_link=details.manage_url,
            fields=fields,
            text=_get_exposed_token_description(details.token_type),
            footer="Canarytokens",
            footer_icon=CANARY_LOGO_ROUND_PUBLIC_URL,
            ts=details.exposed_time.timestamp(),
            color=HexColor.WARNING.value,
        )
    ]
    return TokenAlertDetailsSlack(
        attachments=attachments,
    )


def _data_to_slack_fields(data: dict[str, Union[str, dict]]) -> list[SlackField]:
    fields: list[SlackField] = []
    for label, value in data.items():
        if not label or not value:
            continue

        message_text = json.dumps(value) if isinstance(value, dict) else value
        fields.append(
            SlackField(
                title=prettify_snake_case(label),
                value=message_text,
                short=len(max(message_text.split("\n"))) < MAX_INLINE_LENGTH,
            )
        )

    return fields


class SlackField(BaseModel):
    title: str
    value: str
    short: bool = True


class SlackAttachment(BaseModel):
    title: str = "Canarytoken Triggered"
    title_link: Optional[HttpUrl] = None
    mrkdwn_in: List[str] = ["title"]
    fallback: str = ""
    fields: List[SlackField]
    text: Optional[str] = None
    footer: Optional[str] = None
    footer_icon: Optional[HttpUrl] = None
    ts: Optional[int] = None
    color: Optional[str] = None

    def __init__(self, **data: Any) -> None:
        # HACK: We can do better here.
        title = data.get("title", "Canarytoken Triggered")
        title_link_str = f": {data['title_link']}" if "title_link" in data else ""
        data["fallback"] = f"{title}{title_link_str}"
        super().__init__(**data)


class TokenAlertDetailsSlack(BaseModel):
    """Details that are sent to slack webhooks."""

    attachments: List[SlackAttachment]

    def json_safe_dict(self) -> Dict[str, str]:
        return json_safe_dict(self)


class TokenAlertDetailGeneric(TokenAlertDetails):
    ...


class TokenExposedDetailGeneric(TokenExposedDetails):
    ...


def _get_exposed_token_description(token_type: TokenTypes) -> str:
    return TOKEN_EXPOSED_DESCRIPTION.format(
        readable_type=readable_token_type_names[token_type]
    )
