import datetime
import os
import pytest
import json
from pathlib import Path

import sys

sys.path.insert(0, "lambda_source")
os.environ["ZENDESK_EXPOSED_TICKET_TAG"] = "test_tag"
os.environ["ZENDESK_CLOSED_TICKET_TAG"] = "test_close_tag"
os.environ["ZENDESK_ASSIGNEE"] = "0000"
os.environ["TOKENS_SERVERS_ALLOW_LIST"] = (
    "example.com,example.net,example-test.org,example2.com,example2.net,example-test-domain.org"
)

from exposed_key_checker.ticket_manager import TicketData  # noqa: E402
from exposed_key_checker.exposed_keys import (  # noqa: E402
    parse_tickets,
    get_recent_open_tickets,
)


def test_parsing(all_tickets: list[TicketData]):
    """
    Tickets should be successfully parsed
    """
    data, _, error_ids = parse_tickets(all_tickets)

    assert error_ids == []
    assert len(data) == 6

    iam_users = [d.iam_user for d in data]
    access_keys = [d.access_key for d in data]
    public_locations = [d.public_location for d in data]
    case_numbers = [d.case_no for d in data]

    assert iam_users == [
        "example.com@@abcdefghijklmnopqrstuvwx1",
        "example.net@@abcdefghijklmnopqrstuvwx2",
        "example-test.org@@abcdefghijklmnopqrstuvwx3",
        "example2.com@@abcdefghijklmnopqrstuvwx4",
        "example2.net@@abcdefghijklmnopqrstuvwx5",
        "example-test-domain.org@@abcdefghijklmnopqrstuvwx6",
    ]

    assert access_keys == [
        "aka1b2c3d4e5f6g7h8i1",
        "aka1b2c3d4e5f6g7h8i2",
        "aka1b2c3d4e5f6g7h8i3",
        "aka1b2c3d4e5f6g7h8i4",
        "aka1b2c3d4e5f6g7h8i5",
        "aka1b2c3d4e5f6g7h8i6",
    ]

    assert public_locations == [
        "https://github.com/testorg/test-project/blob/abcdefg123450572a58f802fa79f84321983d332/folder1/file.js",
        "https://github.com/testorg/test-project/blob/abcdefg123450572a58f802fa79f84321983d332/folder1/random-file",
        "https://github.com/testorg/test-project/blob/abcdefg123450572a58f802fa79f84321983d332/folder1/creds",
        "https://github.com/testorg/test-project/blob/abcdefg123450572a58f802fa79f84321983d332/folder1/aws_test",
        "https://github.com/testorg/test-project/blob/abcdefg123450572a58f802fa79f84321983d332/folder1/README.md",
        "https://github.com/testorg/test-project/blob/abcdefg123450572a58f802fa79f84321983d332/folder1/.aws/credentials",
    ]

    assert case_numbers == [
        "111111111111111",
        "222222222222222",
        "333333333333333",
        "444444444444444",
        "555555555555555",
        "666666666666666",
    ]


def test_get_recent_open_tickets():
    """
    Only tickets that are recent (7 days old or less) and not "closed" or "solved" should be parsed
    """
    tickets = [
        TicketData(
            url="http://example.com",
            id=512,
            created_at=datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            updated_at=datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            status="open",
            subject="some text",
            description="a ticket we expect to include",
        ),
        TicketData(
            url="http://example.com",
            id=512,
            created_at=datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            updated_at=datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            status="closed",
            subject="some text",
            description="A closed ticket",
        ),
        TicketData(
            url="http://example.com",
            id=512,
            created_at=datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            updated_at=datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            status="solved",
            subject="some text",
            description="A solved ticket",
        ),
        TicketData(
            url="http://example.com",
            id=512,
            created_at=(
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(days=8)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            updated_at=(
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(days=8)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            status="open",
            subject="some text",
            description="a ticket that's too old to be considered",
        ),
    ]
    tickets_in_window = get_recent_open_tickets(tickets)
    assert len(tickets_in_window) == 1


def test_ignore_keywords(ignore_tickets: list[TicketData]):
    """
    The ignored tickets should not be parsed, but shouldn't error either (this is for emails like AWS following up on a case.)
    """
    data, _, error_ids = parse_tickets(ignore_tickets)
    assert data == []
    assert error_ids == []


def test_parse_failure():
    """
    Tickets that cannot be parsed and are not ignored should be added to the list of error IDs.
    """
    tickets = [
        TicketData(
            url="http://example.com",
            id=512,
            created_at="2024-07-11T11:06:04Z",
            updated_at="2024-07-11T11:06:04Z",
            status="open",
            subject="invalid",
            description="invalid",
        )
    ]
    data, _, error_ids = parse_tickets(tickets)

    assert data == []
    assert error_ids == [512]


def test_url_parsing(all_tickets: list[TicketData]):
    """
    Each URL should be at least 10 chars long and have a TLD
    """
    data, _, _ = parse_tickets(all_tickets)
    tickets_with_short_locations = {
        d.ticket.id for d in data if len(d.public_location) <= 20
    }
    tickets_without_tlds = {
        d.ticket.id for d in data if not _has_tld(d.public_location)
    }

    assert tickets_with_short_locations == set()
    assert tickets_without_tlds == set()


@pytest.fixture()
def valid_tickets() -> list[TicketData]:
    path = Path.cwd() / "tests" / "test_data_to_parse.json"
    data = json.loads(path.read_text())

    return [TicketData(**d) for d in data]


@pytest.fixture()
def ignore_tickets() -> list[TicketData]:
    path = Path.cwd() / "tests" / "test_data_to_ignore.json"
    data = json.loads(path.read_text())

    tickets = []
    for k in data:
        tickets.extend([TicketData(**d) for d in data[k]])

    return tickets


@pytest.fixture()
def all_tickets(
    valid_tickets: list[TicketData], ignore_tickets: list[TicketData]
) -> list[TicketData]:
    return valid_tickets + ignore_tickets


def _has_tld(location: str) -> bool:
    tld_list = [".com", ".net", ".org"]
    return any(tld in location for tld in tld_list)
