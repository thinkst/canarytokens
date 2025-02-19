from typing import Generator
from dataclasses import dataclass
from datetime import datetime
import os
import requests

ZENDESK_EXPOSED_TICKET_TAG = os.environ["ZENDESK_EXPOSED_TICKET_TAG"]
ZENDESK_CLOSED_TICKET_TAG = os.environ["ZENDESK_CLOSED_TICKET_TAG"]
ZENDESK_ASSIGNEE = os.environ["ZENDESK_ASSIGNEE"]


class ZendeskTicketManager:
    ZENDESK_SEARCH_LAST_PAGE = (
        10  # the search endpoint has a maximum number of pages that it allows
    )

    def __init__(self, api_token: str, user: str, api_base_url: str):
        self._auth = (user, api_token)
        self._api_base_url = api_base_url

    def read_all_tickets_in_batches(self) -> "Generator[list[TicketData], None, None]":
        next_url = f"{self._api_base_url}/api/v2/search.json"
        for _ in range(self.ZENDESK_SEARCH_LAST_PAGE):
            if next_url is None:
                break

            tickets, next_url = self.get_tickets_from_api(next_url)
            yield tickets

    def get_tickets_from_api(
        self,
        url: str | None = None,
    ) -> "tuple[list[TicketData], str | None]":
        r = requests.get(
            url or f"{self._api_base_url}/api/v2/search.json",
            auth=self._auth,
            data={
                "query": f'tags:"{ZENDESK_EXPOSED_TICKET_TAG}"',
                "sort_by": "created_at",
                "sort_order": "desc",
            },
        )

        r.raise_for_status()
        res = r.json()

        tickets = [TicketData.from_dict(t) for t in res["results"]]
        return tickets, res["next_page"]

    def set_ticket_as_solved(self, ticket: "TicketData"):
        print(f"Ticket to set to solved: {ticket.id}")

        url = f"{self._api_base_url}/api/v2/tickets/update_many.json?ids={ticket.id}"

        headers = {"Content-Type": "application/json"}

        payload = {
            "ticket": {
                "status": "solved",
                "assignee_id": ZENDESK_ASSIGNEE,
                "comment": {
                    "body": "Resolved by AWS key checker lambda.",
                    "public": True,
                },
                "additional_tags": ["closed-by-aws-exposed-key-checker"],
            }
        }

        response = requests.put(url, headers=headers, json=payload, auth=self._auth)
        if response.status_code == 200:
            print("Ticket successfully updated to solved and tag added.")
        else:
            print(f"Failed to update ticket. Status code: {response.status_code}")
            print(f"Response: {response.text}")


@dataclass
class TicketData:
    url: str
    id: int
    created_at: str
    updated_at: str
    status: str
    subject: str
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> "TicketData":
        return cls(
            data["url"],
            data["id"],
            data["created_at"],
            data["updated_at"],
            data["status"],
            data["subject"],
            "".join(data["description"].splitlines()),
        )

    @property
    def created_dt(self) -> datetime:
        return datetime.strptime(self.created_at, "%Y-%m-%dT%H:%M:%SZ")
