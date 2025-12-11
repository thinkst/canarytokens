from __future__ import annotations
from typing import Union, Optional, Literal
import json
from enum import Enum
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum  # Python 3.11+
else:
    from backports.strenum import StrEnum  # Python < 3.11
import re
from functools import partial
from datetime import datetime

from pydantic import BaseModel, HttpUrl, parse_obj_as, validator, Field

from canarytokens import constants
from canarytokens.utils import json_safe_dict, prettify_snake_case, dict_to_csv
from canarytokens.models import (
    READABLE_TOKEN_TYPE_NAMES,
    Memo,
    TokenTypes,
    TokenAlertDetails,
    TokenExposedDetails,
)

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


class DecimalColor(Enum):
    WARNING = HexColor.WARNING.decimal_value
    ERROR = HexColor.ERROR.decimal_value
    CANARY_GREEN = HexColor.CANARY_GREEN.decimal_value


class WebhookType(StrEnum):
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
        return _format_as_googlechat_canaryalert(details)
    elif webhook_type == WebhookType.DISCORD:
        return _format_as_discord_canaryalert(details)
    elif webhook_type == WebhookType.MS_TEAMS:
        return _format_as_ms_teams_canaryalert(details)
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
        return _format_as_googlechat_token_exposed(details)
    elif webhook_type == WebhookType.DISCORD:
        return _format_as_discord_token_exposed(details)
    elif webhook_type == WebhookType.MS_TEAMS:
        return _format_as_ms_teams_token_exposed(details)
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
        card = GoogleChatCard(
            header=GoogleChatHeader(
                title="Validating new Canarytokens webhook",
                imageUrl=CANARY_LOGO_ROUND_PUBLIC_URL,
                imageType="CIRCLE",
                imageAltText="Thinkst Canary",
            ),
            sections=[],
        )
        return TokenAlertDetailsGoogleChat(
            cardsV2=[GoogleChatCardV2(cardId="unique-card-id", card=card)]
        )
    elif webhook_type == WebhookType.DISCORD:
        embeds = DiscordEmbeds(
            author=DiscordAuthorField(icon_url=CANARY_LOGO_ROUND_PUBLIC_URL),
            url=WEBHOOK_TEST_URL,
            title="Validating new Canarytokens webhook",
            fields=[],
            timestamp=datetime.now(),
        )
        return TokenAlertDetailsDiscord(embeds=[embeds])
    elif webhook_type == WebhookType.MS_TEAMS:
        columns = [
            MsTeamsColumn(
                items=[
                    MsTeamsColumnItem(
                        type="TextBlock",
                        text="Validating new Canarytokens webhook",
                        weight="Bolder",
                        size="Large",
                    )
                ]
            )
        ]

        return TokenAlertDetailsMsTeams(
            attachments=[
                TokenAlertAttachmentMsTeams(
                    content=TokenAlertContentMsTeams(
                        body=[MsTeamsColumnSet(columns=columns)],
                        actions=[
                            MsTeamsAction(
                                type="Action.OpenUrl",
                                title="Canarytokens.org",
                                url="https://canarytokens.org/nest/",
                                iconUrl=CANARY_LOGO_ROUND_PUBLIC_URL,
                            )
                        ],
                    )
                )
            ]
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


def _format_as_googlechat_canaryalert(
    details: TokenAlertDetails,
) -> TokenAlertDetailsGoogleChat:
    # construct google chat alert , top section
    top_section = GoogleChatSection(
        header="Alert Details",
        widgets=_data_to_googlechat_text_widgets(
            {
                "channel": details.channel,
                "time": details.time.strftime("%Y-%m-%d %H:%M:%S (UTC)"),
                "canarytoken": details.token,
                "token_reminder": details.memo,
            }
        ),
    )

    # construct google chat alert , additional section
    additional_widgets: list[GoogleChatTextWithTopLabel] = []
    if details.src_data:
        additional_widgets.extend(_data_to_googlechat_text_widgets(details.src_data))
    if details.additional_data:
        additional_widgets.extend(
            _data_to_googlechat_text_widgets(details.additional_data)
        )

    additional_widgets.append(
        GoogleChatButtonList(
            buttons=[
                GoogleChatButton(
                    text="Manage token",
                    url=details.manage_url,
                    material_icon="settings",
                )
            ]
        )
    )
    additional_section = GoogleChatSection(
        header="Additional Details", widgets=additional_widgets
    )

    # construct google chat alert card
    card = GoogleChatCard(
        header=GoogleChatHeader(
            title="Canarytoken Triggered",
            imageUrl=CANARY_LOGO_ROUND_PUBLIC_URL,
            imageType="CIRCLE",
            imageAltText="Thinkst Canary",
        ),
        sections=[top_section, additional_section],
    )
    # make google chat payload
    return TokenAlertDetailsGoogleChat(
        cardsV2=[GoogleChatCardV2(cardId="unique-card-id", card=card)]
    )


def _format_as_googlechat_token_exposed(
    details: TokenExposedDetails,
) -> TokenAlertDetailsGoogleChat:
    card = GoogleChatCardV2(
        cardId="unique-card-id",
        card=GoogleChatCard(
            header=GoogleChatHeader(
                title="Canarytoken Exposed",
                imageUrl=CANARY_LOGO_ROUND_PUBLIC_URL,
                imageType="CIRCLE",
                imageAltText="Thinkst Canary",
            ),
            sections=[
                GoogleChatSection(
                    widgets=[
                        GoogleChatParagraph(
                            text=_get_exposed_token_description(details.token_type)
                        )
                    ]
                ),
                GoogleChatSection(
                    header="Exposure Details",
                    widgets=[
                        GoogleChatColumns(
                            column_items=[
                                GoogleChatColumnItems(
                                    widgets=[
                                        GoogleChatTextWithTopLabel(
                                            top_label="Key ID", text=details.key_id
                                        ),
                                        GoogleChatTextWithTopLabel(
                                            top_label="Key exposed here",
                                            text=f'<a href="{details.public_location}">{details.public_location}</a>',
                                        ),
                                    ]
                                ),
                                GoogleChatColumnItems(
                                    widgets=[
                                        GoogleChatTextWithTopLabel(
                                            top_label="Token Reminder",
                                            text=details.memo,
                                        ),
                                        GoogleChatTextWithTopLabel(
                                            top_label="Key exposed at",
                                            text=details.exposed_time.strftime(
                                                "%Y-%m-%d %H:%M:%S (UTC)"
                                            ),
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        GoogleChatButtonList(
                            buttons=[
                                GoogleChatButton(
                                    text="Manage token",
                                    url=details.manage_url,
                                    material_icon="settings",
                                )
                            ]
                        ),
                    ],
                ),
            ],
        ),
    )

    return TokenAlertDetailsGoogleChat(cardsV2=[card])


def _data_to_googlechat_text_widgets(
    data: dict[str, str],
) -> list[GoogleChatTextWithTopLabel]:
    widgets: list[GoogleChatTextWithTopLabel] = []
    for label, text in data.items():
        if not label or not text:
            continue

        message_text = json.dumps(text) if isinstance(text, dict) else "{}".format(text)
        widgets.append(
            GoogleChatTextWithTopLabel(
                text=message_text, top_label=prettify_snake_case(label)
            )
        )

    return widgets


class GoogleChatWidget(BaseModel):
    ...


class GoogleChatParagraph(GoogleChatWidget):
    text: str

    def dict(self, *args, **kwargs):
        return {"textParagraph": {"text": self.text}}


class GoogleChatTextWithTopLabel(GoogleChatWidget):
    text: str
    top_label: Optional[str] = None

    def dict(self, *args, **kwargs):
        d = {"decoratedText": {"text": self.text}}
        if self.top_label:
            d["decoratedText"]["topLabel"] = self.top_label

        return d


class GoogleChatButton(BaseModel):
    text: str
    url: HttpUrl
    material_icon: Optional[str] = None
    alt_text: Optional[str] = None

    def dict(self, *args, **kwargs):
        d = {"text": self.text, "onClick": {"openLink": {"url": self.url}}}
        if self.material_icon:
            d["icon"] = {
                "materialIcon": {"name": self.material_icon},
                "altText": self.alt_text or self.text.lower(),
            }

        return d


class GoogleChatButtonList(GoogleChatWidget):
    buttons: list[GoogleChatButton]

    def dict(self, *args, **kwargs):
        return {"buttonList": {"buttons": [button.dict() for button in self.buttons]}}


class GoogleChatColumnItems(BaseModel):
    widgets: list[GoogleChatWidget]
    horizontalSizeStyle: str = "FILL_MINIMUM_SPACE"
    horizontalAlignment: str = "START"
    verticalAlignment: str = "CENTER"

    def dict(self, *args, **kwargs):
        return {
            "horizontalSizeStyle": self.horizontalSizeStyle,
            "horizontalAlignment": self.horizontalAlignment,
            "verticalAlignment": self.verticalAlignment,
            "widgets": [widget.dict() for widget in self.widgets],
        }


class GoogleChatColumns(GoogleChatWidget):
    column_items: list[GoogleChatColumnItems]

    def dict(self, *args, **kwargs):
        return {"columns": {"columnItems": [ci.dict() for ci in self.column_items]}}


class GoogleChatHeader(BaseModel):
    title: str = "Canarytoken Triggered"
    imageUrl: HttpUrl
    imageType: str = "CIRCLE"
    imageAltText: str = "Thinkst Canary"


class GoogleChatSection(BaseModel):
    header: str = ""
    collapsible: bool = False
    widgets: list[GoogleChatWidget] = []


class GoogleChatCard(BaseModel):
    header: GoogleChatHeader
    sections: list[GoogleChatSection] = []


class GoogleChatCardV2(BaseModel):
    cardId: str = "unique-card-id"
    card: GoogleChatCard


class TokenAlertDetailsGoogleChat(BaseModel):
    cardsV2: list[GoogleChatCardV2]

    def json_safe_dict(self) -> dict[str, str]:
        return json_safe_dict(self)


def _format_as_discord_canaryalert(
    details: TokenAlertDetails,
) -> TokenAlertDetailsDiscord:
    embeds = DiscordEmbeds(
        author=DiscordAuthorField(
            icon_url=CANARY_LOGO_ROUND_PUBLIC_URL,
        ),
        url=details.manage_url,
        timestamp=details.time.strftime("%Y-%m-%dT%H:%M:%S"),
        color=DecimalColor.ERROR.value,
    )

    embeds.add_fields(
        {
            "canarytoken": details.token,
            "token_reminder": details.memo,
            "src_data": details.src_data if details.src_data else None,
        }
    )

    if details.additional_data:
        embeds.add_fields(details.additional_data)

    embeds.add_fields({"Manage token": details.manage_url})

    return TokenAlertDetailsDiscord(embeds=[embeds])


def _format_as_discord_token_exposed(
    details: TokenExposedDetails,
) -> TokenAlertDetailsDiscord:
    embeds = DiscordEmbeds(
        author=DiscordAuthorField(
            icon_url=CANARY_LOGO_ROUND_PUBLIC_URL,
        ),
        url=details.manage_url,
        timestamp=details.exposed_time.strftime("%Y-%m-%dT%H:%M:%S"),
        description=_get_exposed_token_description(details.token_type),
        color=DecimalColor.WARNING.value,
    )

    embeds.add_fields(
        {
            "Key ID": details.key_id,
            "Token Reminder": details.memo,
            "Key exposed here": details.public_location,
            "Manage token": details.manage_url,
        }
    )

    return TokenAlertDetailsDiscord(embeds=[embeds])


class DiscordFieldEntry(BaseModel):
    name: str = ""
    value: str = ""
    inline: bool = False


class DiscordAuthorField(BaseModel):
    name: str = "Canary Alerts"
    icon_url: str


class DiscordEmbeds(BaseModel):
    author: DiscordAuthorField
    color: int = DecimalColor.CANARY_GREEN.value
    title: str = "Canarytoken Triggered"
    description: Optional[str] = None
    url: Optional[HttpUrl]
    timestamp: datetime
    fields: list[DiscordFieldEntry] = []

    def add_fields(self, fields_info: dict[str, str]) -> None:
        for label, text in fields_info.items():
            if not label or not text:
                continue

            message_text = (
                f"```{json.dumps(text)}```"
                if isinstance(text, dict)
                else "{}".format(text)
            )
            self.fields.append(
                DiscordFieldEntry(
                    name=prettify_snake_case(label),
                    value=message_text,
                    inline=len(max(message_text.split("\n"))) < MAX_INLINE_LENGTH,
                )
            )

    @validator("timestamp", pre=True)
    def validate_timestamp(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        return value

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S"),
        }


class TokenAlertDetailsDiscord(BaseModel):
    """Details that are sent to Discord webhooks"""

    embeds: list[DiscordEmbeds]

    def json_safe_dict(self) -> dict[str, str]:
        return json_safe_dict(self)


def _format_as_ms_teams_canaryalert(
    details: TokenAlertDetails,
) -> TokenAlertDetailsMsTeams:
    columns = [
        MsTeamsColumn(
            items=[
                MsTeamsColumnItem(
                    type="Image", url=CANARY_LOGO_ROUND_PUBLIC_URL, size="Medium"
                )
            ]
        ),
        MsTeamsColumn(
            items=[
                MsTeamsColumnItem(
                    type="TextBlock",
                    text="Canarytoken Triggered",
                    weight="Bolder",
                    size="ExtraLarge",
                )
            ]
        ),
    ]

    facts = []
    if details.src_data:
        facts.extend(_data_to_ms_teams_facts(details.src_data))
    if details.additional_data:
        facts.extend(_data_to_ms_teams_facts(details.additional_data))

    body: list[Union[MsTeamsColumnSet, MsTeamsFactSet]] = [
        MsTeamsColumnSet(columns=columns),
        MsTeamsFactSet(facts=facts),
    ]

    return TokenAlertDetailsMsTeams(
        attachments=[
            TokenAlertAttachmentMsTeams(
                content=TokenAlertContentMsTeams(
                    body=body,
                    actions=[
                        MsTeamsAction(
                            type="Action.OpenUrl",
                            title="⚙️ Manage token",
                            url=details.manage_url,
                        ),
                        MsTeamsAction(
                            type="Action.OpenUrl",
                            title="Canarytokens.org",
                            url="https://canarytokens.org/nest/",
                            iconUrl=CANARY_LOGO_ROUND_PUBLIC_URL,
                        ),
                    ],
                )
            )
        ]
    )


def _format_as_ms_teams_token_exposed(
    details: TokenExposedDetails,
) -> TokenAlertDetailsMsTeams:
    columns = [
        MsTeamsColumn(
            items=[
                MsTeamsColumnItem(
                    type="Image", url=CANARY_LOGO_ROUND_PUBLIC_URL, size="Medium"
                )
            ]
        ),
        MsTeamsColumn(
            items=[
                MsTeamsColumnItem(
                    type="TextBlock",
                    text="Canarytoken Exposed",
                    weight="Bolder",
                    size="ExtraLarge",
                )
            ]
        ),
    ]

    text = MsTeamsTextblock(text=_get_exposed_token_description(details.token_type))

    facts = [
        MsTeamsFact(title="Key ID", value=details.key_id),
        MsTeamsFact(title="Token Reminder", value=details.memo),
        MsTeamsFact(
            title="Key exposed at",
            value=details.exposed_time.strftime("%Y-%m-%d %H:%M:%S (UTC)"),
        ),
        MsTeamsFact(title="Key exposed here", value=details.public_location),
    ]

    body: list[Union[MsTeamsColumnSet, MsTeamsTextblock, MsTeamsFactSet]] = [
        MsTeamsColumnSet(columns=columns),
        text,
        MsTeamsFactSet(facts=facts),
    ]
    return TokenAlertDetailsMsTeams(
        attachments=[
            TokenAlertAttachmentMsTeams(
                content=TokenAlertContentMsTeams(
                    body=body,
                    actions=[
                        MsTeamsAction(
                            type="Action.OpenUrl",
                            title="⚙️ Manage token",
                            url=details.manage_url,
                        ),
                        MsTeamsAction(
                            type="Action.OpenUrl",
                            title="Canarytokens.org",
                            url="https://canarytokens.org/nest/",
                            iconUrl=CANARY_LOGO_ROUND_PUBLIC_URL,
                        ),
                    ],
                )
            )
        ]
    )


def _data_to_ms_teams_facts(data: dict[str, Union[str, dict]]) -> list[MsTeamsFact]:
    facts: list[MsTeamsFact] = []

    for label, value in data.items():
        if not label or not value:
            continue

        message_text = dict_to_csv(value) if isinstance(value, dict) else value
        facts.append(MsTeamsFact(title=prettify_snake_case(label), value=message_text))

    return facts


class MsTeamsTextblock(BaseModel):
    type: str = "TextBlock"
    text: str
    wrap: bool = True


class MsTeamsAction(BaseModel):
    type: str
    title: str
    url: HttpUrl = None
    iconUrl: HttpUrl = None


class MsTeamsFact(BaseModel):
    title: str
    value: str


class MsTeamsFactSet(BaseModel):
    type: str = "FactSet"
    facts: Optional[list[MsTeamsFact]] = None


class MsTeamsColumnItem(BaseModel):
    type: str
    text: str = None
    weight: str = None
    url: HttpUrl = None
    size: str


class MsTeamsColumn(BaseModel):
    type: str = "Column"
    width: str = "auto"
    horizontalAlignment: str = "Left"
    items: Optional[list[MsTeamsColumnItem]] = None


class MsTeamsColumnSet(BaseModel):
    type: Literal["ColumnSet"] = "ColumnSet"
    columns: Optional[list[MsTeamsColumn]] = None


class TokenAlertContentMsTeams(BaseModel):
    schema_: str = Field(
        "https://adaptivecards.io/schemas/adaptive-card.json", alias="$schema"
    )
    type: str = "AdaptiveCard"
    version: str = "1.5"
    body: Optional[
        list[Union[MsTeamsColumnSet, MsTeamsFactSet, MsTeamsTextblock]]
    ] = None
    actions: Optional[list[MsTeamsAction]] = None


class TokenAlertAttachmentMsTeams(BaseModel):
    contentType: str = "application/vnd.microsoft.teams.card.o365connector"
    content: TokenAlertContentMsTeams


class TokenAlertDetailsMsTeams(BaseModel):
    attachments: list[TokenAlertAttachmentMsTeams]

    def json_safe_dict(self) -> dict[str, str]:
        return self.dict(by_alias=True, exclude_none=True)


class TokenAlertDetailGeneric(TokenAlertDetails):
    ...


class TokenExposedDetailGeneric(TokenExposedDetails):
    ...


def _get_exposed_token_description(token_type: TokenTypes) -> str:
    return TOKEN_EXPOSED_DESCRIPTION.format(
        readable_type=READABLE_TOKEN_TYPE_NAMES[token_type]
    )
