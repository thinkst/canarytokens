from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from exposed_key_checker.ticket_manager import TicketData

MAX_PROCESS_AGE_DAYS = 7


def get_recent_open_tickets(tickets):
    return [
        ticket
        for ticket in tickets
        if (datetime.now() - ticket.created_dt) <= timedelta(days=MAX_PROCESS_AGE_DAYS)
        and ticket.status not in ["solved", "closed"]
    ]


def parse_tickets(
    tickets: "list[TicketData]",
) -> "tuple[list[ExposedKeyData], list[int]]":
    exposed_data: list[ExposedKeyData] = []
    ignorable_tickets: list[int] = []
    parse_error_ids: list[int] = []
    for ticket in tickets:
        data = ExposedKeyData.from_ticket(ticket)
        ignorable = _should_ignore_ticket_parse_failure(ticket)
        if ignorable:
            ignorable_tickets.append(ticket.id)
        elif data is None:
            parse_error_ids.append(ticket.id)
        else:
            exposed_data.append(data)

    return exposed_data, ignorable_tickets, parse_error_ids


def _should_ignore_ticket_parse_failure(ticket: TicketData) -> bool:
    """
    Ignore ticket parse failures if we don't expect the email to have iam_user / key details

    There are a few different types of emails, like follow up emails, case resolved emails, etc.
    """
    ignore_strs = [
        "correspondence was added to case",
        "following up",
        "following-up",
        "follow up",
        "follow-up",
        "previous notice",
        "we have not heard back from you",
        "duplicate of case",
        "case has been resolved",
    ]

    text = ticket.description.lower()
    for match_str in ignore_strs:
        if match_str in text:
            return True
    return False


@dataclass
class ExposedKeyData:
    ticket: TicketData
    iam_user: str
    access_key: str
    public_location: str
    case_no: str

    @property
    def tokens_server(self) -> str:
        return self.iam_user.split("@@")[0]

    @property
    def token(self) -> str:
        return self.iam_user.split("@@")[1]

    @classmethod
    def from_ticket(cls, ticket: TicketData) -> "ExposedKeyData | None":
        iam_user = ""
        access_key = ""
        location = ""
        case_no = "<unknown>"

        account_details_match = re.search(
            r"access key * (\w+).*user *([\w-]+\.(?:com|net|org)@@\w+)",
            ticket.description,
            re.IGNORECASE,
        )
        if account_details_match is None:
            return None

        access_key, iam_user = account_details_match.groups()

        case_match = re.search(r"case (\d+)", ticket.subject, re.IGNORECASE)
        if case_match is not None:
            case_no = case_match.group(1)

        location_match = re.search(
            r"online at *(http[s]?://[\w%./#-]+) *\. *(?:to)?",
            ticket.description,
            re.IGNORECASE,
        )
        if location_match is not None:
            location = location_match.group(1)

        return cls(ticket, iam_user.lower(), access_key.lower(), location, case_no)

    def __str__(self) -> str:
        return f"<Key with IAM user = {self.iam_user}, key = {self.access_key} and ticket ID = {self.ticket.id}>"

    def __repr__(self) -> str:
        return self.__str__()
