from typing import Generator
from dataclasses import dataclass
from datetime import datetime
import os
import requests

ZENDESK_EXPOSED_TICKET_TAG = os.environ["ZENDESK_EXPOSED_TICKET_TAG"]


class ZendeskTicketManager:
    ZENDESK_SEARCH_LAST_PAGE = (
        10  # the search endpoint has a maximum number of pages that it allows
    )

    def __init__(self, api_token: str, user: str, search_endpoint: str):
        self._auth = (user, api_token)
        self._search_endpoint = search_endpoint

    def read_all_tickets_in_batches(self) -> "Generator[list[TicketData], None, None]":
        next_url = self._search_endpoint
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
            url or self._search_endpoint,
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


@dataclass
class TicketData:
    url: str
    id: int
    created_at: str
    updated_at: str
    subject: str
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> "TicketData":
        return cls(
            data["url"],
            data["id"],
            data["created_at"],
            data["updated_at"],
            data["subject"],
            "".join(data["description"].splitlines()),
        )

    @property
    def created_dt(self) -> datetime:
        return datetime.strptime(self.created_at, "%Y-%m-%dT%H:%M:%SZ")
