from enum import IntEnum, StrEnum

from pydantic import HttpUrl
import requests


class Priority(IntEnum):
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class Team(StrEnum):
    PRODUCT = "product-dev@thinkst.com"


class Service(StrEnum):
    CANARYTOKENS = "canarytokens"


def ticket(
    *,
    ticket_url: HttpUrl,
    subject: str,
    category: str,
    customer: str,
    text: str,
    dedupe_key: str,
    team: Team = Team.PRODUCT,
    priority: Priority = Priority.NORMAL,
    service: Service = Service.CANARYTOKENS,
) -> None:
    data = {
        "subject": f"{subject} on {customer}",
        "category": category,
        "customer": customer,
        "team": team.value,
        "priority": str(priority.value),
        "text": text,
        "dedupe_key": dedupe_key,
        "service": service.value,
    }
    response = requests.post(str(ticket_url), json=data, timeout=30)
    response.raise_for_status()
