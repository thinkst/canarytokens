#!/usr/bin/env python3
import argparse
from collections import defaultdict
import datetime
import json
import logging
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Canarytokens settings paths are relative to the process working directory.
if __name__ == "__main__":
    os.chdir(PROJECT_ROOT / "frontend")

from pydantic import EmailStr, TypeAdapter, HttpUrl, parse_obj_as  # noqa: E402

from canarytokens import credit_card_v2, queries, ticketing  # noqa: E402
from canarytokens.channel_output_email import (  # noqa: E402
    EmailResponseStatuses,
    send_email,
)
from canarytokens.exceptions import NoCanarydropFound  # noqa: E402
from canarytokens.redismanager import DB  # noqa: E402
from canarytokens.settings import SwitchboardSettings  # noqa: E402
from canarytokens.tokens import Canarytoken  # noqa: E402
from canarytokens.utils import get_autoescaped_env  # noqa: E402


logger = logging.getLogger("credit-card-expiry-mail-run")
EXPIRY_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
JINJA2_ENV = get_autoescaped_env(str(PROJECT_ROOT / "templates"))
email_validator = TypeAdapter(EmailStr)


def timestamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(EXPIRY_TIME_FORMAT)


def credit_card_expiry_mail_run(  # noqa: C901
    year: int,
    month: int,
    switchboard_settings: SwitchboardSettings,
) -> dict:
    log_record = {
        "status": "failed",
        "expiry": f"{year:04}{month:02}",
        "timestamps": {"start": timestamp()},
        "credit_card_tokens": {
            "not_found": [],
            "marked_sent": [],
            "to_send": [],
            "webhook_only": [],
        },
        "mail_received": [],
        "persistence_errors": {},
        "send_errors": {},
    }

    try:
        datetime.date(year, month, 1)
    except (TypeError, ValueError):
        log_record["error_message"] = "Invalid expiry"
        log_record["timestamps"]["end"] = timestamp()
        return log_record

    try:
        status, cards = credit_card_v2.get_expiring_cards(year * 100 + month)
    except Exception as error:
        log_record["error_message"] = f"{error.__class__.__name__}: {error}"
        log_record["timestamps"]["end"] = timestamp()
        return log_record

    if status != credit_card_v2.Status.SUCCESS or cards is None:
        log_record["error_message"] = (
            f"Failed to retrieve expiring cards: {status.value}"
        )
        log_record["timestamps"]["end"] = timestamp()
        return log_record

    cards_by_recipient = defaultdict(list)
    for card in cards:
        canarytoken = card["canarytoken"]
        try:
            canarydrop = queries.get_canarydrop(Canarytoken(canarytoken))
        except NoCanarydropFound:
            log_record["credit_card_tokens"]["not_found"].append(canarytoken)
            continue

        if canarydrop.cc_v2_expiry_reminder_sent:
            log_record["credit_card_tokens"]["marked_sent"].append(canarytoken)
            continue

        if not canarydrop.alert_email_enabled or not canarydrop.alert_email_recipient:
            log_record["credit_card_tokens"]["webhook_only"].append(canarytoken)
            continue

        recipient = canarydrop.alert_email_recipient.lower()
        cards_by_recipient[recipient].append(canarydrop)
        log_record["credit_card_tokens"]["to_send"].append(canarytoken)

    subject = "Your Credit Card Canarytokens Expire This Month"
    html_template = JINJA2_ENV.get_template(
        "emails/_generated_dont_edit_notification_credit_card_expiry.html"
    )
    text_template = JINJA2_ENV.get_template(
        "emails/notification_credit_card_expiry.txt"
    )

    for recipient, recipient_drops in cards_by_recipient.items():
        template_cards = [
            {
                "memo": canarydrop.memo,
                "canarytoken": canarydrop.canarytoken.value(),
            }
            for canarydrop in recipient_drops
        ]
        try:
            email_response_status, _ = send_email(
                switchboard_settings=switchboard_settings,
                email_recipient=email_validator.validate_python(recipient),
                email_subject=subject,
                email_content_html=html_template.render(cards=template_cards),
                email_content_text=text_template.render(cards=template_cards),
                from_email=switchboard_settings.ALERT_EMAIL_FROM_ADDRESS,
                from_display=switchboard_settings.ALERT_EMAIL_FROM_DISPLAY,
            )
            if email_response_status != EmailResponseStatuses.SENT:
                raise RuntimeError(
                    f"Email provider returned {email_response_status or 'no status'}"
                )
        except Exception as error:
            log_record["send_errors"][recipient] = (
                f"{error.__class__.__name__}: {error}"
            )
            continue

        log_record["mail_received"].append(recipient)
        for canarydrop in recipient_drops:
            canarydrop.cc_v2_expiry_reminder_sent = True
            try:
                queries.save_canarydrop(canarydrop)
            except Exception as error:
                log_record["persistence_errors"][canarydrop.canarytoken.value()] = (
                    f"{error.__class__.__name__}: {error}"
                )

    log_record["timestamps"]["end"] = timestamp()
    if not log_record["send_errors"] and not log_record["persistence_errors"]:
        log_record["status"] = "success"
    return log_record


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Send grouped credit card Canarytoken expiry reminders. This script is "
            "safe to rerun because cards are marked after successful delivery."
        )
    )
    parser.add_argument("--year", type=int, help="Expiry year (defaults to UTC now)")
    parser.add_argument("--month", type=int, help="Expiry month (defaults to UTC now)")
    args = parser.parse_args()

    if (args.year is None) != (args.month is None):
        parser.error("--year and --month must be provided together")
    if args.year is None:
        now = datetime.datetime.now(datetime.timezone.utc)
        args.year = now.year
        args.month = now.month
    return args


def ticket_failed_mail_run(
    log_record: dict,
    switchboard_settings: SwitchboardSettings | None,
) -> None:
    ticket_url = (
        switchboard_settings.TICKET_URL
        if switchboard_settings is not None
        else os.getenv("CANARY_TICKET_URL")
    )
    if ticket_url is None:
        return

    customer = (
        switchboard_settings.PUBLIC_DOMAIN
        if switchboard_settings is not None
        else os.getenv("CANARY_PUBLIC_DOMAIN", "canarytokens")
    )
    ticket_log_record = {
        **log_record,
        "credit_card_tokens": {
            key: len(value) if isinstance(value, list) else value
            for key, value in log_record.get("credit_card_tokens", {}).items()
        },
    }
    ticketing.ticket(
        ticket_url=parse_obj_as(HttpUrl, ticket_url),
        subject="Credit Card Expiry Mail Run Failed",
        category="credit-card-expiry-mail-run-failed",
        customer=customer,
        text=(
            "The Credit Card Canarytoken expiry reminder mail run failed.\n\n"
            "Inspect the run record and rerun the expiry mailer if reminders were "
            "not sent.\n\n"
            "Run record:\n\n```\n"
            f"{json.dumps(ticket_log_record, default=str, indent=2, sort_keys=True)}"
            "\n```"
        ),
        dedupe_key=f"credit-card-expiry-mail-run-failed-{customer}",
        priority=ticketing.Priority.NORMAL,
    )


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    switchboard_settings = None
    try:
        switchboard_settings = SwitchboardSettings()
        DB.set_db_details(
            hostname=switchboard_settings.REDIS_HOST,
            port=switchboard_settings.REDIS_PORT,
        )
        log_record = credit_card_expiry_mail_run(
            year=args.year,
            month=args.month,
            switchboard_settings=switchboard_settings,
        )
    except Exception as error:
        log_record = {
            "status": "failed",
            "expiry": f"{args.year:04}{args.month:02}",
            "timestamps": {"start": timestamp(), "end": timestamp()},
            "error_message": f"{error.__class__.__name__}: {error}",
        }

    logger.info("Expiry mail-run (Log record): %s", log_record)
    print(json.dumps(log_record, default=str, indent=2, sort_keys=True))

    if log_record["status"] != "success":
        ticket_failed_mail_run(log_record, switchboard_settings)

    return 0 if log_record["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
