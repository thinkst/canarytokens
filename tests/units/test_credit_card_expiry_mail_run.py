import json
from types import SimpleNamespace

import pytest
from pydantic import HttpUrl

from canarytokens import credit_card_v2
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel_output_email import EmailResponseStatuses
from canarytokens.exceptions import NoCanarydropFound
from canarytokens.models import TokenTypes
from canarytokens.settings import SwitchboardSettings
from canarytokens.tokens import Canarytoken
from scripts import credit_card_expiry_mail_run


def make_drop(
    *,
    recipient="owner@example.com",
    email_enabled=True,
    memo="card memo",
    reminder_sent=None,
):
    return Canarydrop(
        canarytoken=Canarytoken(),
        type=TokenTypes.CREDIT_CARD_V2,
        memo=memo,
        alert_email_enabled=email_enabled,
        alert_email_recipient=recipient,
        cc_v2_expiry_reminder_sent=reminder_sent,
    )


def test_expiry_reminder_state_is_only_serialized_after_sending():
    canarydrop = make_drop()

    assert "cc_v2_expiry_reminder_sent" not in canarydrop.serialize()

    canarydrop.cc_v2_expiry_reminder_sent = True

    assert canarydrop.serialize()["cc_v2_expiry_reminder_sent"] == "True"


def test_mail_run_groups_cards_continues_after_failure_and_is_idempotent(
    monkeypatch,
    settings: SwitchboardSettings,
):
    first = make_drop(recipient="Owner@example.com", memo="first")
    second = make_drop(recipient="owner@example.com", memo="second")
    failed = make_drop(recipient="failed@example.com", memo="failed")
    already_sent = make_drop(recipient="sent@example.com", reminder_sent=True)
    webhook_only = make_drop(recipient=None, email_enabled=False)
    drops = {
        drop.canarytoken.value(): drop
        for drop in [first, second, failed, already_sent, webhook_only]
    }
    deleted_token = Canarytoken().value()
    cards = [
        {"canarytoken": token, "card_id": f"card-{index}", "expiry": 202608}
        for index, token in enumerate([*drops, deleted_token])
    ]
    sent_messages = []
    saved_drops = []

    monkeypatch.setattr(
        credit_card_expiry_mail_run.credit_card_v2,
        "get_expiring_cards",
        lambda expiry: (credit_card_v2.Status.SUCCESS, cards),
    )

    def get_canarydrop(canarytoken):
        try:
            return drops[canarytoken.value()]
        except KeyError:
            raise NoCanarydropFound

    def send_email(**kwargs):
        sent_messages.append(kwargs)
        if kwargs["email_recipient"] == "failed@example.com":
            return EmailResponseStatuses.ERROR, ""
        return EmailResponseStatuses.SENT, "message-id"

    monkeypatch.setattr(
        credit_card_expiry_mail_run.queries, "get_canarydrop", get_canarydrop
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run.queries,
        "save_canarydrop",
        saved_drops.append,
    )
    monkeypatch.setattr(credit_card_expiry_mail_run, "send_email", send_email)

    record = credit_card_expiry_mail_run.credit_card_expiry_mail_run(
        year=2026,
        month=8,
        switchboard_settings=settings,
    )

    assert record["status"] == "failed"
    assert record["mail_received"] == ["owner@example.com"]
    assert list(record["send_errors"]) == ["failed@example.com"]
    assert record["credit_card_tokens"]["not_found"] == [deleted_token]
    assert record["credit_card_tokens"]["marked_sent"] == [
        already_sent.canarytoken.value()
    ]
    assert record["credit_card_tokens"]["webhook_only"] == [
        webhook_only.canarytoken.value()
    ]
    assert first.cc_v2_expiry_reminder_sent is True
    assert second.cc_v2_expiry_reminder_sent is True
    assert failed.cc_v2_expiry_reminder_sent is None
    assert saved_drops == [first, second]
    assert len(sent_messages) == 2
    owner_message = next(
        message
        for message in sent_messages
        if message["email_recipient"] == "owner@example.com"
    )
    assert "first" in owner_message["email_content_text"]
    assert "second" in owner_message["email_content_text"]

    sent_messages.clear()
    monkeypatch.setattr(
        credit_card_expiry_mail_run,
        "send_email",
        lambda **kwargs: (
            sent_messages.append(kwargs) or EmailResponseStatuses.SENT,
            "message-id",
        ),
    )

    rerun_record = credit_card_expiry_mail_run.credit_card_expiry_mail_run(
        year=2026,
        month=8,
        switchboard_settings=settings,
    )

    assert rerun_record["status"] == "success"
    assert rerun_record["mail_received"] == ["failed@example.com"]
    assert len(sent_messages) == 1
    assert sent_messages[0]["email_recipient"] == "failed@example.com"
    assert failed.cc_v2_expiry_reminder_sent is True


def test_mail_run_reports_expiry_query_failure(
    monkeypatch,
    settings: SwitchboardSettings,
):
    monkeypatch.setattr(
        credit_card_expiry_mail_run.credit_card_v2,
        "get_expiring_cards",
        lambda expiry: (credit_card_v2.Status.ERROR, None),
    )

    record = credit_card_expiry_mail_run.credit_card_expiry_mail_run(
        year=2026,
        month=8,
        switchboard_settings=settings,
    )

    assert record["status"] == "failed"
    assert record["error_message"] == "Failed to retrieve expiring cards: error"


def test_mail_run_rejects_invalid_expiry(settings: SwitchboardSettings):
    record = credit_card_expiry_mail_run.credit_card_expiry_mail_run(
        year=2026,
        month=13,
        switchboard_settings=settings,
    )

    assert record["status"] == "failed"
    assert record["error_message"] == "Invalid expiry"


def test_main_tickets_failed_run(
    monkeypatch,
    settings: SwitchboardSettings,
):
    configured_settings = settings.copy(
        update={"TICKET_URL": HttpUrl("https://ticket.example/ticket", scheme="https")}
    )
    ticket_calls = []
    failed_record = {
        "status": "failed",
        "expiry": "202608",
        "error_message": "mail failed",
    }

    monkeypatch.setattr(
        credit_card_expiry_mail_run,
        "parse_args",
        lambda: SimpleNamespace(year=2026, month=8),
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run,
        "SwitchboardSettings",
        lambda: configured_settings,
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run.DB,
        "set_db_details",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run,
        "credit_card_expiry_mail_run",
        lambda **kwargs: failed_record,
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run.ticketing,
        "ticket",
        lambda **kwargs: ticket_calls.append(kwargs),
    )

    exit_code = credit_card_expiry_mail_run.main()

    assert exit_code == 1
    assert len(ticket_calls) == 1
    assert (
        ticket_calls[0]["priority"]
        == credit_card_expiry_mail_run.ticketing.Priority.NORMAL
    )
    assert ticket_calls[0]["category"] == "credit-card-expiry-mail-run-failed"
    assert ticket_calls[0]["dedupe_key"] == (
        "credit-card-expiry-mail-run-failed-127.0.0.1"
    )


def test_ticket_uses_token_counts_without_mutating_log_record(
    monkeypatch,
    settings: SwitchboardSettings,
):
    configured_settings = settings.copy(
        update={"TICKET_URL": HttpUrl("https://ticket.example/ticket", scheme="https")}
    )
    log_record = {
        "status": "failed",
        "credit_card_tokens": {
            "not_found": ["missing-token"],
            "marked_sent": ["sent-token-1", "sent-token-2"],
            "to_send": ["pending-token"],
            "webhook_only": [],
        },
    }
    ticket_calls = []
    monkeypatch.setattr(
        credit_card_expiry_mail_run.ticketing,
        "ticket",
        lambda **kwargs: ticket_calls.append(kwargs),
    )

    credit_card_expiry_mail_run.ticket_failed_mail_run(log_record, configured_settings)

    ticket_json = ticket_calls[0]["text"].split("```\n", 1)[1].rsplit("\n```", 1)[0]
    ticket_record = json.loads(ticket_json)
    assert ticket_record["credit_card_tokens"] == {
        "not_found": 1,
        "marked_sent": 2,
        "to_send": 1,
        "webhook_only": 0,
    }
    assert log_record["credit_card_tokens"]["not_found"] == ["missing-token"]


def test_main_records_ticket_failure(
    monkeypatch,
    settings: SwitchboardSettings,
):
    failed_record = {"status": "failed", "expiry": "202608"}
    monkeypatch.setattr(
        credit_card_expiry_mail_run,
        "parse_args",
        lambda: SimpleNamespace(year=2026, month=8),
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run,
        "SwitchboardSettings",
        lambda: settings,
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run.DB,
        "set_db_details",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run,
        "credit_card_expiry_mail_run",
        lambda **kwargs: failed_record,
    )

    with pytest.raises(RuntimeError, match="CANARY_TICKET_URL is not configured"):
        credit_card_expiry_mail_run.main()


def test_main_tickets_settings_failure_from_environment(monkeypatch):
    ticket_calls = []

    def fail_settings():
        raise RuntimeError("settings failed")

    monkeypatch.setenv("CANARY_TICKET_URL", "https://ticket.example/ticket")
    monkeypatch.setenv("CANARY_PUBLIC_DOMAIN", "tokens.example")
    monkeypatch.setattr(
        credit_card_expiry_mail_run,
        "parse_args",
        lambda: SimpleNamespace(year=2026, month=8),
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run,
        "SwitchboardSettings",
        fail_settings,
    )
    monkeypatch.setattr(
        credit_card_expiry_mail_run.ticketing,
        "ticket",
        lambda **kwargs: ticket_calls.append(kwargs),
    )

    exit_code = credit_card_expiry_mail_run.main()

    assert exit_code == 1
    assert len(ticket_calls) == 1
    assert ticket_calls[0]["customer"] == "tokens.example"
    assert (
        ticket_calls[0]["priority"]
        == credit_card_expiry_mail_run.ticketing.Priority.NORMAL
    )
