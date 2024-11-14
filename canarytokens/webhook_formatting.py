from __future__ import annotations
import json
from typing import Union, Literal
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
            blocks=[
                SlackHeader(
                    text=SlackTextObject(
                        text="Validating new Canarytokens webhook", type="plain_text"
                    )
                ),
                SlackFooter(),
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
    blocks: list[SlackBlock] = []
    blocks.append(
        SlackHeader(
            text=SlackTextObject(
                type="plain_text",
                text=":red_circle: Canarytoken Triggered :red_circle:",
            )
        )
    )

    blocks.append(
        SlackSection(
            fields=[
                SlackTextWithLabel("Channel", details.channel),
                SlackTextWithLabel("Token Reminder", details.memo),
            ]
        )
    )

    blocks.append(
        SlackSection(
            fields=[
                SlackTextWithLabel(
                    "Time", details.time.strftime("%Y-%m-%d %H:%M:%S (UTC)")
                )
            ]
        )
    )

    if details.src_data:
        blocks.extend(_data_to_slack_blocks(details.src_data))
    if details.additional_data:
        blocks.extend(_data_to_slack_blocks(details.additional_data))

    blocks.append(
        SlackSectionText(
            text=SlackTextObject(text=f":gear: *<{details.manage_url}|Manage token>*")
        )
    )
    blocks.append(SlackFooter())

    return TokenAlertDetailsSlack(blocks=blocks)


def _format_as_slack_token_exposed(
    details: TokenExposedDetails,
) -> TokenAlertDetailsSlack:
    blocks: list[SlackBlock] = []

    blocks.append(
        SlackHeader(
            text=SlackTextObject(
                type="plain_text",
                text=":large_orange_circle: Canarytoken Exposed :large_orange_circle:",
            )
        )
    )

    blocks.append(
        SlackRichText(text=_get_exposed_token_description(details.token_type))
    )
    blocks.append(SlackDivider())

    blocks.append(
        SlackSection(
            fields=[
                SlackTextWithLabel("Token Reminder", details.memo),
                SlackTextWithLabel("Key ID", details.key_id),
            ]
        )
    )

    blocks.append(
        SlackSection(
            fields=[
                SlackTextWithLabel(
                    "Key exposed at",
                    details.exposed_time.strftime("%Y-%m-%d %H:%M:%S (UTC)"),
                )
            ]
        )
    )

    fields = [SlackTextObject(text=f":gear: *<{details.manage_url}|Manage token>*")]
    if details.public_location:
        fields.insert(
            0,
            SlackTextObject(
                text=f":link: *<{details.public_location}|View exposed key>*"
            ),
        )

    blocks.append(SlackSection(fields=fields))
    blocks.append(SlackFooter())

    return TokenAlertDetailsSlack(blocks=blocks)


def _data_to_slack_blocks(data: dict[str, Union[str, dict]]) -> list[SlackBlock]:
    blocks: list[SlackBlock] = []
    for label, value in data.items():
        if (
            not label or not value or label in ["time_hm", "time_ymd"]
        ):  # We already display the time
            continue

        blocks.append(SlackRichText(text=prettify_snake_case(label)).set_bold())
        if isinstance(value, dict):
            blocks.append(SlackRichText(text=json.dumps(value)).set_code_block())
        else:
            blocks.append(SlackRichText(text=value))

    return blocks


class SlackTextObject(BaseModel):
    type: Union[Literal["plain_text"], Literal["mrkdwn"]] = "mrkdwn"
    text: str


class SlackTextWithLabel(SlackTextObject):
    def __init__(self, label: str, text: str):
        super().__init__(text=f"*{label}*\n{text}")


class SlackBlock(BaseModel):
    ...


class SlackHeader(SlackBlock):
    type = "header"
    text: SlackTextObject


class SlackRichText(SlackBlock):
    text: str
    bold = False
    rich_text_type: Union[
        Literal["rich_text_section"], Literal["rich_text_preformatted"]
    ] = "rich_text_section"

    def set_code_block(self):
        self.rich_text_type = "rich_text_preformatted"
        return self

    def set_bold(self):
        self.bold = True
        return self

    def dict(self, *_args, **__kwargs):
        text = {"type": "text", "text": self.text}
        if self.bold is True:
            text["style"] = {"bold": True}

        return {
            "type": "rich_text",
            "elements": [{"type": self.rich_text_type, "elements": [text]}],
        }


class SlackFooter(SlackBlock):
    def dict(self, *_args, **_kwargs):
        return {
            "type": "context",
            "elements": [
                {
                    "type": "image",
                    "image_url": CANARY_LOGO_ROUND_PUBLIC_URL,
                    "alt_text": "images",
                },
                {
                    "type": "mrkdwn",
                    "text": "<https://canarytokens.org|Canarytokens.org>",
                },
            ],
        }


class SlackDivider(SlackBlock):
    type = "divider"


class SlackSection(SlackBlock):
    type = "section"
    fields: list[SlackTextObject]


class SlackSectionText(SlackBlock):
    type = "section"
    text: SlackTextObject


class TokenAlertDetailsSlack(BaseModel):
    """Details that are sent to slack webhooks."""

    blocks: list[SlackBlock]

    def json_safe_dict(self) -> dict[str, str]:
        return json_safe_dict(self)


class TokenAlertDetailGeneric(TokenAlertDetails):
    ...


class TokenExposedDetailGeneric(TokenExposedDetails):
    ...


def _get_exposed_token_description(token_type: TokenTypes) -> str:
    return TOKEN_EXPOSED_DESCRIPTION.format(
        readable_type=readable_token_type_names[token_type]
    )
