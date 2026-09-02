from datetime import datetime
from typing import Literal, Union
import pytest
from canarytokens.models import Memo, TokenAlertDetails, TokenExposedDetails, TokenTypes
from canarytokens.webhook_formatting import (
    GoogleChatButton,
    GoogleChatButtonList,
    GoogleChatCard,
    GoogleChatCardV2,
    GoogleChatColumnItems,
    GoogleChatColumns,
    GoogleChatHeader,
    GoogleChatParagraph,
    GoogleChatSection,
    GoogleChatTextWithTopLabel,
    SlackDivider,
    SlackFooter,
    SlackHeader,
    SlackRichText,
    SlackSection,
    SlackSectionText,
    SlackTextObject,
    TokenAlertDetailsSlack,
    WebhookType,
    format_details_for_webhook,
    get_webhook_type,
    TokenAlertDetailGeneric,
    TokenAlertDetailsGoogleChat,
    TokenAlertDetailsDiscord,
    TokenAlertDetailsMsTeams,
    TokenExposedDetailGeneric,
)


@pytest.mark.parametrize(
    ["url", "expected_type"],
    [
        (
            "https://hooks.slack.com/services/A0B1C2D3E/A0B1C2D3E4F/a0B1c2D3e4F5g6H7i8J9k0L1",
            WebhookType.SLACK,
        ),
        (
            "https://discord.com/api/webhooks/0123456789012345678/ABCDEFGHIJKLMNOPQRST_NB14QRp-iybHHFMtYKW8v76CqxnR69HV9tG5HrrVEo3BT9P",
            WebhookType.DISCORD,
        ),
        (
            "https://chat.googleapis.com/v1/spaces/AAAAabcdefg/messages?key=ABCDEFGHIJKLMNOPQRTSTU-AbCdEfGhIjKlMnOp&token=1a2b3c4d_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            WebhookType.GOOGLE_CHAT,
        ),
        (
            "https://default12345678abcdef.ac.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/12345678abcdef/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=12345678abcdef",
            WebhookType.MS_TEAMS,
        ),
        ("http://example.com/abc", WebhookType.GENERIC),
    ],
)
def test_get_webhook_type(url: str, expected_type: WebhookType):
    assert get_webhook_type(url) == expected_type


@pytest.mark.parametrize(
    ["details_type", "webhook_type", "expected_payload_type"],
    [
        ("alert", WebhookType.GENERIC, TokenAlertDetailGeneric),
        ("exposed", WebhookType.GENERIC, TokenExposedDetailGeneric),
        ("alert", WebhookType.SLACK, TokenAlertDetailsSlack),
        ("exposed", WebhookType.SLACK, TokenAlertDetailsSlack),
        ("alert", WebhookType.GOOGLE_CHAT, TokenAlertDetailsGoogleChat),
        ("exposed", WebhookType.GOOGLE_CHAT, TokenAlertDetailsGoogleChat),
        ("alert", WebhookType.DISCORD, TokenAlertDetailsDiscord),
        ("exposed", WebhookType.DISCORD, TokenAlertDetailsDiscord),
        ("alert", WebhookType.MS_TEAMS, TokenAlertDetailsMsTeams),
        ("exposed", WebhookType.MS_TEAMS, TokenAlertDetailsMsTeams),
    ],
)
def test_format_details_for_webhook_alert_type(
    details_type: Union[Literal["alert"], Literal["exposed"]],
    webhook_type: WebhookType,
    expected_payload_type,
):
    """
    format_details_for_webhook should return the correct payload type based on the webhook type
    """
    if details_type == "alert":
        details = TokenAlertDetails(
            time=datetime.now(),
            memo=Memo("test"),
            additional_data=None,
            manage_url="http://example.com",
        )
    else:
        details = TokenExposedDetails(
            token_type=TokenTypes.AWS_KEYS,
            token="",
            memo=Memo("test"),
            key_id="",
            public_location="",
            exposed_time=datetime.now(),
            manage_url="http://example.com",
        )

    payload = format_details_for_webhook(webhook_type, details)
    assert isinstance(payload, expected_payload_type)


def test_slack_payload_serialization():
    payload = TokenAlertDetailsSlack(
        blocks=[
            SlackHeader(text=SlackTextObject(type="plain_text", text="Header")),
            SlackDivider(),
            SlackSection(fields=[SlackTextObject(text="Field")]),
            SlackSectionText(text=SlackTextObject(text="Section")),
            SlackRichText(text="Rich text").set_bold(),
            SlackFooter(),
        ]
    ).json_safe_dict()

    assert payload["blocks"][:5] == [
        {"type": "header", "text": {"type": "plain_text", "text": "Header"}},
        {"type": "divider"},
        {"type": "section", "fields": [{"type": "mrkdwn", "text": "Field"}]},
        {"type": "section", "text": {"type": "mrkdwn", "text": "Section"}},
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Rich text",
                            "style": {"bold": True},
                        }
                    ],
                }
            ],
        },
    ]
    assert payload["blocks"][5]["type"] == "context"


def test_slack_payload_coerces_numeric_additional_data_to_text():
    details = TokenAlertDetails(
        time=datetime.now(),
        memo=Memo("test"),
        additional_data={"status_code": 200},
        manage_url="http://example.com",
    )

    payload = format_details_for_webhook(WebhookType.SLACK, details).json_safe_dict()

    assert payload["blocks"][4]["elements"][0]["elements"][0]["text"] == "200"


def test_google_chat_payload_serialization():
    payload = TokenAlertDetailsGoogleChat(
        cardsV2=[
            GoogleChatCardV2(
                card=GoogleChatCard(
                    header=GoogleChatHeader(imageUrl="https://example.com/logo.png"),
                    sections=[
                        GoogleChatSection(
                            widgets=[
                                GoogleChatParagraph(text="Paragraph"),
                                GoogleChatTextWithTopLabel(
                                    text="Text", top_label="Label"
                                ),
                                GoogleChatButtonList(
                                    buttons=[
                                        GoogleChatButton(
                                            text="Manage", url="https://example.com"
                                        )
                                    ]
                                ),
                                GoogleChatColumns(
                                    column_items=[
                                        GoogleChatColumnItems(
                                            widgets=[GoogleChatParagraph(text="Nested")]
                                        )
                                    ]
                                ),
                            ]
                        )
                    ],
                )
            )
        ]
    ).json_safe_dict()

    widgets = payload["cardsV2"][0]["card"]["sections"][0]["widgets"]
    assert widgets[0] == {"textParagraph": {"text": "Paragraph"}}
    assert widgets[1] == {"decoratedText": {"text": "Text", "topLabel": "Label"}}
    assert widgets[2] == {
        "buttonList": {
            "buttons": [
                {
                    "text": "Manage",
                    "onClick": {"openLink": {"url": "https://example.com/"}},
                }
            ]
        }
    }
    assert widgets[3]["columns"]["columnItems"][0]["widgets"] == [
        {"textParagraph": {"text": "Nested"}}
    ]
