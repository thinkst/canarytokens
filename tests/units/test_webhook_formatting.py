from datetime import datetime
from typing import Literal, Union
import pytest
from canarytokens.models import Memo, TokenAlertDetails, TokenExposedDetails, TokenTypes
from canarytokens.webhook_formatting import (
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
            "https://azurebasethinkst.webhook.office.com/webhookb2/aaaaaaaa-bbbb-cccc-dddd-111111111111@aaaaaaaa-bbbb-cccc-dddd-111111111111/IncomingWebhook/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/bbbbbbbb-cccc-dddd-1111-eeeeeeeeeeee/ABCDEFG123456789ABCDEFG123456789abcdefg1234567",
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
