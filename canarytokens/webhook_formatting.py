from __future__ import annotations
from typing import Union
from enum import Enum
import re
from functools import partial
from datetime import datetime

from pydantic import HttpUrl, parse_obj_as

from canarytokens import constants
from canarytokens.channel import (
    format_as_discord_canaryalert,
    format_as_googlechat_canaryalert,
    format_as_ms_teams_canaryalert,
    format_as_slack_canaryalert,
)
from canarytokens.models import (
    Memo,
    TokenTypes,
    TokenAlertDetails,
    TokenExposedDetails,
)


WEBHOOK_TEST_URL = parse_obj_as(HttpUrl, "http://example.com/test/url/for/webhook")


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
        return format_as_slack_canaryalert(details)
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
        raise NotImplementedError(
            f"_format_exposed_details_for_webhook not implemented for webhook type: {webhook_type}"
        )
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
        raise NotImplementedError(
            "generate_webhook_test_payload not implemented for SLACK"
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


class TokenAlertDetailGeneric(TokenAlertDetails):
    ...


class TokenExposedDetailGeneric(TokenExposedDetails):
    ...
