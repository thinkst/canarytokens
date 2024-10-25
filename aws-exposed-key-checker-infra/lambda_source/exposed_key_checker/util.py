import os
import requests


def create_support_ticket(subject: str, text: str, dedupe_key: str):
    ticket_service_url = os.getenv("TICKET_SERVICE_URL")
    ticket_service_recipient = os.getenv("TICKET_SERVICE_RECIPIENT")

    data = {
        "subject": subject,
        "team": ticket_service_recipient,
        "text": text,
        "dedupe_key": dedupe_key,
    }

    print(f"Creating support ticket with data: {data}.")

    if not ticket_service_url or not ticket_service_recipient:
        print("Ticket service not configured, skipping actual ticket request.")
        return

    res = requests.post(ticket_service_url, json=data)
    res.raise_for_status()
