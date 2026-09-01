from unittest import mock

from pydantic import HttpUrl

from canarytokens import ticketing


@mock.patch("canarytokens.ticketing.requests.post", autospec=True)
def test_ticket_posts_console_compatible_payload(mock_post):
    response = mock_post.return_value

    ticketing.ticket(
        ticket_url=HttpUrl("https://ticket.example/ticket", scheme="https"),
        subject="Mail Run Failed",
        category="mail-run-failed",
        customer="tokens.example",
        text="Failure details",
        dedupe_key="mail-run-failed-tokens.example",
    )

    mock_post.assert_called_once_with(
        "https://ticket.example/ticket",
        json={
            "subject": "Mail Run Failed on tokens.example",
            "category": "mail-run-failed",
            "customer": "tokens.example",
            "team": "product-dev@thinkst.com",
            "priority": "3",
            "text": "Failure details",
            "dedupe_key": "mail-run-failed-tokens.example",
            "service": "canarytokens",
        },
        timeout=30,
    )
    response.raise_for_status.assert_called_once_with()
