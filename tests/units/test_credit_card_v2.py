import io
import json
from types import SimpleNamespace

from canarytokens import credit_card_v2


def test_get_expiring_cards_page_invokes_expiry_lambda(monkeypatch):
    settings = SimpleNamespace(
        CREDIT_CARD_TOKEN_ENABLED=True,
        CREDIT_CARD_INFRA_CUSTOMER_GUID="customer-guid",
        CREDIT_CARD_INFRA_CUSTOMER_SECRET="customer-secret",
    )
    invoke_calls = []

    def invoke_lambda(lambda_name, payload):
        invoke_calls.append((lambda_name, payload))
        return {
            "Payload": io.BytesIO(
                json.dumps(
                    {
                        "status": "success",
                        "body": {
                            "cards": [{"canarytoken": "token-1"}],
                            "next_token": {"CardId": {"S": "card-1"}},
                        },
                    }
                ).encode()
            )
        }

    monkeypatch.setattr(credit_card_v2, "frontend_settings", settings)
    monkeypatch.setattr(credit_card_v2, "_invoke_lambda", invoke_lambda)

    status, body = credit_card_v2._get_expiring_cards(
        expiry=202608,
        next_token={"CardId": {"S": "previous-card"}},
    )

    assert status == credit_card_v2.Status.SUCCESS
    assert body["cards"] == [{"canarytoken": "token-1"}]
    assert invoke_calls == [
        (
            "ExpiryReminderService",
            {
                "api": "/expiry/list",
                "guid": "customer-guid",
                "secret": "customer-secret",
                "expiry": 202608,
                "limit": 1000,
                "next_token": {"CardId": {"S": "previous-card"}},
            },
        )
    ]


def test_get_expiring_cards_collects_all_pages(monkeypatch):
    responses = iter(
        [
            (
                credit_card_v2.Status.SUCCESS,
                {"cards": [{"canarytoken": "token-1"}], "next_token": "next"},
            ),
            (
                credit_card_v2.Status.SUCCESS,
                {"cards": [{"canarytoken": "token-2"}], "next_token": None},
            ),
        ]
    )
    calls = []

    def get_page(**kwargs):
        calls.append(kwargs)
        return next(responses)

    monkeypatch.setattr(credit_card_v2, "_get_expiring_cards", get_page)

    status, cards = credit_card_v2.get_expiring_cards(202608)

    assert status == credit_card_v2.Status.SUCCESS
    assert cards == [
        {"canarytoken": "token-1"},
        {"canarytoken": "token-2"},
    ]
    assert calls == [
        {"expiry": 202608, "next_token": None},
        {"expiry": 202608, "next_token": "next"},
    ]
