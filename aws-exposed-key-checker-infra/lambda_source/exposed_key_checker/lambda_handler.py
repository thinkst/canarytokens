import json
import os
from datetime import datetime, timedelta
import requests
import boto3
from botocore.config import Config

from exposed_key_checker.database import Database
from exposed_key_checker.ticket_manager import ZendeskTicketManager
from exposed_key_checker.exposed_keys import ExposedKeyData, parse_tickets
from exposed_key_checker import support_ticketer

DB_TABLE_NAME = "ExposedKeyCheckerProcessed"
MAX_PROCESS_AGE_DAYS = 7
ZENDESK_EXPOSED_TICKET_TAG = os.environ["ZENDESK_EXPOSED_TICKET_TAG"]
ZENDESK_AUTH_SECRET_ID = os.environ["ZENDESK_AUTH_SECRET_ID"]
TOKENS_SERVERS_ALLOW_LIST = [
    s.strip() for s in os.environ["TOKENS_SERVERS_ALLOW_LIST"].split(",")
]
TOKENS_POST_URL_OVERRIDE = os.getenv("TOKENS_POST_URL_OVERRIDE")

BOTO_CONFIG = Config(region_name="us-east-1")


def lambda_handler(_event, _context):
    db = Database()

    try:
        ticket_manager = ZendeskTicketManager(*get_zendesk_auth())
        key_data, failed_ids = gather_data(ticket_manager)
    except Exception as e:
        text = f"The key checker could not query the Zendesk API for tickets.\nThe exception was {e}."
        support_ticketer.create_ticket(
            "Exposed AWS Key Checker could not query the Zendesk API",
            text,
            "exposed-aws-key-checker-zendesk-api-error",
        )
        return

    process_data(db, key_data)

    if failed_ids:
        text = f"The key checker could not parse the following Zendesk ticket IDs: {failed_ids}"
        support_ticketer.create_ticket(
            "Exposed AWS Key Checker could not parse Zendesk tickets",
            text,
            "exposed-aws-key-checker-parse-error",
        )


def process_data(db: Database, data: "list[ExposedKeyData]"):
    unprocessed_items = [d for d in data if not db.has_key_been_processed(d)]
    processed_count = len(data) - len(unprocessed_items)
    print(f"Skipping {processed_count} items that were already processed.")

    items_to_process = []
    for item in unprocessed_items:
        if item.tokens_server not in TOKENS_SERVERS_ALLOW_LIST:
            print(
                f"Ignoring the following item because its server is not in the allow list: {item}"
            )
            continue

        items_to_process.append(item)

    print(f"Processing {len(items_to_process)} unprocessed items: {items_to_process}.")

    for item in items_to_process:
        try:
            send_to_tokens_server(item)
        except Exception as e:
            text = f"The key checker could not post the exposed event to the tokens server for the following item: {item}\nThe exception was: {e}.\n\nThis post will be retried automatically on the next run of the lambda. This only needs to be investigated if the failures continue."
            support_ticketer.create_ticket(
                "Exposed AWS Key Checker could not post to tokens server",
                text,
                "exposed-aws-key-checker-post-error",
            )
        else:
            db.mark_key_as_processed(item)


def gather_data(
    ticket_manager: "ZendeskTicketManager",
) -> "tuple[list[ExposedKeyData], list[int]]":
    data: list[ExposedKeyData] = []
    error_ids: list[int] = []

    num_tickets = 0
    for tickets in ticket_manager.read_all_tickets_in_batches():
        num_tickets += len(tickets)
        key_data, eids = parse_tickets(tickets)
        data.extend(key_data)
        error_ids.extend(eids)

        age = datetime.now() - key_data[-1].ticket.created_dt
        if age > timedelta(days=MAX_PROCESS_AGE_DAYS):
            # Only check the last week's data
            break

    print(f"Got {len(data)} exposed keys from {num_tickets} tickets.")

    return data, error_ids


def send_to_tokens_server(data: "ExposedKeyData"):
    post_url = TOKENS_POST_URL_OVERRIDE or data.tokens_server
    print(f"Sending key exposed event to {post_url} for token {data.token}")

    post_data = {
        "token_exposed": True,
        "exposed_time": int(data.ticket.created_dt.strftime("%s")),
        "public_location": data.public_location,
    }

    res = requests.post(post_url, data=post_data)
    res.raise_for_status()


def get_zendesk_auth():
    client = boto3.client("secretsmanager", config=BOTO_CONFIG)
    res = client.get_secret_value(SecretId=ZENDESK_AUTH_SECRET_ID)
    data = json.loads(res.get("SecretString"))
    return data["api_token"], data["user"], data["search_endpoint"]
