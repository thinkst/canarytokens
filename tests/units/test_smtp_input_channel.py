from collections import Counter
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytest

from twisted.internet.testing import StringTransport
from twisted.mail.smtp import Address, User
from twisted.protocols.basic import LineReceiver

from canarytokens import channel_input_smtp
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel_input_smtp import (
    MAX_ATTACHMENT_PARTS,
    MAX_HEADER_BYTES,
    MAX_HEADER_LINES,
    MAX_RECIPIENTS,
    MAX_STORED_BYTES,
    MAX_STORED_LINES,
    CanaryESMTP,
    CanaryMessage,
    CanarySMTPFactory,
)
from canarytokens.exceptions import NoCanarydropFound
from canarytokens.models import TokenTypes
from canarytokens.queries import get_canarydrop, save_canarydrop
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken
from tests.utils import slack_webhook_test

HEADER_FLOOD_PREFIX = b"X-Pad: "
HEADER_FLOOD_LINE = HEADER_FLOOD_PREFIX + b"B" * (
    LineReceiver.MAX_LENGTH - len(HEADER_FLOOD_PREFIX)
)
HEADER_FLOOD_ATTEMPTS = (MAX_HEADER_BYTES + len(HEADER_FLOOD_LINE) - 1) // len(
    HEADER_FLOOD_LINE
) + 1

switchboard = Switchboard()


def test_canary_message(setup_db):
    """
    Check that CanaryMessage correctly parses lines of an email.
    """
    message = MIMEMultipart()
    message["Subject"] = "Twisted is great!"
    message["From"] = "fromtest@test.com"
    message["To"] = ", ".join(["me@test.com", "you@test.com"])
    with open("data/canary_image.png", mode="rb") as fp:
        part_image = MIMEImage(fp.read())

    link = b"https://some.link/in/email"
    part_text = MIMEText(
        f"This is my super awesome email, sent with Twisted! with a link {link}",
        "plain",
    )
    message.attach(part_text)
    message.attach(part_image)

    cm = CanaryMessage(esmtp=None, canarydrop=None)
    for line in message.as_string().splitlines():
        cm.lineReceived(line=line.encode())
    links_found = cm.links_re.findall(b"\r\n".join(cm.lines))

    assert len(cm.attachments) == 3
    assert len(links_found) == 1
    assert links_found[0] == link
    assert all(
        o in cm.headers
        for o in [
            b"Subject: Twisted is great!",
            b"From: fromtest@test.com",
            b"To: me@test.com, you@test.com",
        ]
    )


async def test_canary_esmtp(frontend_settings, settings, setup_db):
    """
    A shot-gun test that sets up an SMTP token, runs the
    ESMTP parsing logic and checks that the resulting hit
    has the expected values.
    A finer grained set of tests would be better.
    """
    # Create token and persist to redis
    cd = Canarydrop(
        generate=True,
        type=TokenTypes.SMTP,
        memo="test SMTP",
        canarytoken=Canarytoken(),
        alert_webhook_enabled=True,
        alert_webhook_url=slack_webhook_test,
    )
    save_canarydrop(cd)
    # Create a CanarySMTPFactory and build the protocol
    # class which is a CanaryESMTP.
    canary_smtp = CanarySMTPFactory(
        switchboard=switchboard,
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
    )
    protocol: CanaryESMTP = canary_smtp.buildProtocol(addr="1.0.0.1")
    canary_smtp.protocol = protocol
    canary_smtp.protocol.transport = StringTransport()
    canary_smtp.protocol.makeConnection(canary_smtp.protocol.transport)

    # Build a multipart message that contains a link,
    # an attached text and image.
    message = MIMEMultipart()
    message["Subject"] = "Twisted is great!"
    message["From"] = "fromtest@test.com"
    message["To"] = ", ".join(["me@test.com", "you@test.com"])
    with open("data/canary_image.png", mode="rb") as fp:
        part_image = MIMEImage(fp.read())

    link = "https://some.link/in/email"
    part_text = MIMEText(
        f"This is my super awesome email, sent with Twisted! with a link {link}",
        "plain",
    )
    message.attach(part_text)
    message.attach(part_image)

    # 'Send' the header.
    canary_smtp.protocol.receivedHeader(
        helo=(b"some.name.come", b"1.0.0.1"),
        recipients=[
            User(
                destination=f"{cd.canarytoken.value()}@test.com",
                helo=b"",
                protocol=canary_smtp.protocol,
                orig="test@test.com",
            )
        ],
        origin=Address("test@test.com"),
    )
    # Validate the To field. This checks we have an associated token
    # for this To address.
    defered_callable = canary_smtp.protocol.validateTo(
        User(
            destination=f"{cd.canarytoken.value()}@test.com",
            helo=b"",
            protocol=canary_smtp.protocol,
            orig="test@test.com",
        )
    )
    # Twisted sends the response to the returned `IMessage`
    # class. Here, we construct the CanaryMessage which implements `Imessage`.
    canary_message = defered_callable()
    # Feed the message line by line.
    for line in message.as_bytes().splitlines():
        canary_message.lineReceived(line)
    # After a message has been received an End-of-Message (oem)
    # is sent which triggers the dispatch.
    canary_message.eomReceived()

    # Check that the created hit has expected values
    assert canary_message.token_hit.input_channel == "SMTP"
    assert len(canary_message.token_hit.mail.links) == 1
    assert link in canary_message.token_hit.mail.links
    assert len(canary_message.token_hit.mail.recipients) == 1
    assert cd.canarytoken.value() in canary_message.token_hit.mail.recipients[0]
    assert len(canary_message.token_hit.mail.headers) == 5


def test_header_flood_bounded_by_bytes():
    cm = CanaryMessage(esmtp=None, canarydrop=None)
    for _ in range(HEADER_FLOOD_ATTEMPTS):
        cm.lineReceived(HEADER_FLOOD_LINE)
    assert cm.header_byte_count >= MAX_HEADER_BYTES
    assert cm.header_byte_count < MAX_HEADER_BYTES + len(HEADER_FLOOD_LINE)


def test_header_flood_bounded_by_line_count():
    cm = CanaryMessage(esmtp=None, canarydrop=None)
    for _ in range(MAX_HEADER_LINES):
        cm.lineReceived(b"X")
    cm.lineReceived(b"X")
    assert len(cm.headers) == MAX_HEADER_LINES


def test_boundary_flood_bounded():
    cm = CanaryMessage(esmtp=None, canarydrop=None)
    cm.lineReceived(b"Content-Type: multipart/mixed; boundary=b")
    cm.lineReceived(b"")
    for _ in range(MAX_STORED_LINES + 1):
        cm.lineReceived(b"b")
    assert len(cm.attachments) == MAX_ATTACHMENT_PARTS
    assert len(cm.lines) == MAX_STORED_LINES
    assert sum(len(a) for a in cm.attachments) <= MAX_STORED_LINES


def test_links_survive_header_flood():
    cm = CanaryMessage(esmtp=None, canarydrop=None)
    for _ in range(HEADER_FLOOD_ATTEMPTS):
        cm.lineReceived(HEADER_FLOOD_LINE)
    cm.lineReceived(b"")
    cm.lineReceived(b"visit https://evil.example/abc now")
    links = cm.links_re.findall(b"\r\n".join(cm.lines))
    assert b"https://evil.example/abc" in links


def test_body_flood_bounded_by_bytes():
    cm = CanaryMessage(esmtp=None, canarydrop=None)
    cm.lineReceived(b"Subject: x")
    cm.lineReceived(b"")
    line = b"B" * (MAX_STORED_BYTES // MAX_STORED_LINES + 1)
    for _ in range(MAX_STORED_LINES + 1):
        cm.lineReceived(line)
    assert cm.stored_byte_count >= MAX_STORED_BYTES
    assert cm.stored_byte_count < MAX_STORED_BYTES + len(line)
    assert len(cm.lines) < MAX_STORED_LINES


def test_body_flood_bounded_by_line_count():
    cm = CanaryMessage(esmtp=None, canarydrop=None)
    cm.lineReceived(b"Subject: x")
    cm.lineReceived(b"")
    for _ in range(MAX_STORED_LINES):
        cm.lineReceived(b"B")
    cm.lineReceived(b"B")
    assert len(cm.lines) == MAX_STORED_LINES
    assert cm.stored_byte_count <= MAX_STORED_LINES


def test_normal_mail_still_parsed():
    cm = CanaryMessage(esmtp=None, canarydrop=None)
    for line in [
        b"From: fromtest@test.com",
        b"Subject: hi",
        b"",
        b"plain body with https://normal.example/ok inside",
    ]:
        cm.lineReceived(line)
    links = cm.links_re.findall(b"\r\n".join(cm.lines))
    assert links == [b"https://normal.example/ok"]
    assert b"Subject: hi" in cm.headers


@pytest.fixture
def smtp_recipient_session(monkeypatch, frontend_settings, settings):
    drops = {}
    saved_hits = []
    dispatched_hits = []

    def lookup(*, canarytoken):
        try:
            return drops[canarytoken.value()]
        except KeyError:
            raise NoCanarydropFound()

    monkeypatch.setattr(channel_input_smtp, "get_canarydrop", lookup)
    monkeypatch.setattr(
        channel_input_smtp.queries,
        "save_canarydrop",
        lambda drop: saved_hits.append(drop.triggered_details.hits[-1]),
    )
    monkeypatch.setattr(channel_input_smtp.queries, "get_geoinfo", lambda **kw: None)
    monkeypatch.setattr(channel_input_smtp.queries, "is_tor_relay", lambda **kw: False)
    factory = CanarySMTPFactory(
        switchboard=Switchboard(),
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
    )
    protocol = factory.buildProtocol(None)
    monkeypatch.setattr(
        protocol, "dispatch", lambda drop, hit: dispatched_hits.append(hit)
    )
    transport = StringTransport()
    protocol.makeConnection(transport)

    def send(command):
        transport.clear()
        protocol.dataReceived(command + b"\r\n")
        return transport.value()

    try:
        assert send(b"EHLO example.test").startswith(b"250")
        assert send(b"MAIL FROM:<sender@example.test>").startswith(b"250")
        yield send, drops, saved_hits, dispatched_hits
    finally:
        protocol.setTimeout(None)
        protocol.connectionLost(None)


def test_smtp_duplicate_recipients_delivered_once(smtp_recipient_session):
    send, drops, saved, dispatched = smtp_recipient_session
    token = Canarytoken()
    drops[token.value()] = Canarydrop(canarytoken=token, type=TokenTypes.SMTP)
    for index in range(MAX_RECIPIENTS):
        address = f"{token.value()}@alias{index % 2}.test"
        assert send(f"RCPT TO:<{address}>".encode()).startswith(b"250")
    assert send(f"RCPT TO:<{address}>".encode()).startswith(b"452")
    assert send(b"DATA").startswith(b"354")
    assert send(b"Subject: duplicate recipients\r\n\r\nbody\r\n.").startswith(b"250")
    assert len(saved) == len(dispatched) == 1
    assert [str(Address(value)) for value in saved[0].mail.recipients] == [
        f"{token.value()}@alias0.test"
    ]
    assert len(drops[token.value()].triggered_details.hits) == 1


def test_smtp_distinct_recipient_capacity(smtp_recipient_session):
    send, drops, saved, dispatched = smtp_recipient_session
    missing = Canarytoken().value()
    assert send(f"RCPT TO:<{missing}@example.test>".encode()).startswith(b"550")
    for _ in range(MAX_RECIPIENTS):
        token = Canarytoken()
        drops[token.value()] = Canarydrop(canarytoken=token, type=TokenTypes.SMTP)
        assert send(f"RCPT TO:<{token.value()}@example.test>".encode()).startswith(
            b"250"
        )
    overflow = Canarytoken()
    drops[overflow.value()] = Canarydrop(canarytoken=overflow, type=TokenTypes.SMTP)
    assert send(f"RCPT TO:<{overflow.value()}@example.test>".encode()).startswith(
        b"452"
    )
    assert send(b"MAIL FROM:<replacement@example.test>").startswith(b"503")
    assert send(f"RCPT TO:<{missing}@example.test>".encode()).startswith(b"452")
    assert send(b"DATA").startswith(b"354")
    assert send(b"Subject: accepted recipients\r\n\r\nbody\r\n.").startswith(b"250")
    assert len(saved) == len(dispatched) == MAX_RECIPIENTS
    assert all(len(hit.mail.recipients) == MAX_RECIPIENTS for hit in saved)
    assert not drops[overflow.value()].triggered_details.hits


@pytest.mark.parametrize(
    "reset", [b"RSET", b"HELO example.test", b"EHLO example.test", b"DATA"]
)
def test_smtp_recipient_state_is_transaction_scoped(smtp_recipient_session, reset):
    send, drops, saved, dispatched = smtp_recipient_session
    token = Canarytoken()
    drops[token.value()] = Canarydrop(canarytoken=token, type=TokenTypes.SMTP)
    for _ in range(MAX_RECIPIENTS):
        assert send(f"RCPT TO:<{token.value()}@first.test>".encode()).startswith(b"250")
    if reset == b"DATA":
        assert send(reset).startswith(b"354")
        assert send(b"Subject: first\r\n\r\nbody\r\n.").startswith(b"250")
    else:
        assert send(reset).startswith(b"250")
    assert send(b"MAIL FROM:<sender@example.test>").startswith(b"250")
    assert send(f"RCPT TO:<{token.value()}@second.test>".encode()).startswith(b"250")
    assert send(b"DATA").startswith(b"354")
    assert send(b"Subject: second\r\n\r\nbody\r\n.").startswith(b"250")
    assert len(saved) == len(dispatched) == (2 if reset == b"DATA" else 1)
    assert [str(Address(value)) for value in saved[-1].mail.recipients] == [
        f"{token.value()}@second.test"
    ]


@pytest.mark.parametrize(
    "recipients,first_type",
    [
        ("AB", TokenTypes.SMTP),
        ("BA", TokenTypes.SMTP),
        ("ABA", TokenTypes.SMTP),
        ("AB", TokenTypes.LEGACY),
    ],
)
def test_smtp_recipient_attribution(
    recipients, first_type, monkeypatch, frontend_settings, settings, setup_db
):
    drops = {
        name: Canarydrop(
            canarytoken=Canarytoken(),
            type=first_type if name == "A" else TokenTypes.SMTP,
            alert_email_enabled=True,
            alert_email_recipient=f"{name.lower()}@example.com",
        )
        for name in "AB"
    }
    for drop in drops.values():
        save_canarydrop(drop)
    monkeypatch.setattr(channel_input_smtp.queries, "get_geoinfo", lambda **kw: None)
    monkeypatch.setattr(channel_input_smtp.queries, "is_tor_relay", lambda **kw: False)
    dispatched = []
    factory = CanarySMTPFactory(
        switchboard=Switchboard(),
        frontend_settings=frontend_settings,
        switchboard_settings=settings,
    )
    protocol = factory.buildProtocol(None)
    monkeypatch.setattr(
        protocol,
        "dispatch",
        lambda drop, hit: dispatched.append(
            (drop.canarytoken.value(), drop.alert_email_recipient)
        ),
    )
    transport = StringTransport()
    protocol.makeConnection(transport)

    def send(command):
        transport.clear()
        protocol.dataReceived(command + b"\r\n")
        return transport.value()

    try:
        assert send(b"EHLO example.test").startswith(b"250")
        assert send(b"MAIL FROM:<sender@example.test>").startswith(b"250")
        for name in recipients:
            address = f"{drops[name].canarytoken.value()}@example.test"
            assert send(f"RCPT TO:<{address}>".encode()).startswith(b"250")
        assert send(b"DATA").startswith(b"354")
        assert send(b"Subject: attribution\r\n\r\nbody\r\n.").startswith(b"250")
        for drop in drops.values():
            stored = get_canarydrop(drop.canarytoken)
            assert stored.type == TokenTypes.SMTP
            assert len(stored.triggered_details.hits) == 1
        assert Counter(dispatched) == Counter(
            (drop.canarytoken.value(), drop.alert_email_recipient)
            for drop in drops.values()
        )

        updated = get_canarydrop(drops["A"].canarytoken)
        updated.alert_email_recipient = "updated@example.com"
        save_canarydrop(updated)
        assert send(b"MAIL FROM:<sender@example.test>").startswith(b"250")
        address = f"{updated.canarytoken.value()}@example.test"
        assert send(f"RCPT TO:<{address}>".encode()).startswith(b"250")
        assert send(b"DATA").startswith(b"354")
        assert send(b"Subject: next message\r\n\r\nbody\r\n.").startswith(b"250")
        assert dispatched[-1] == (updated.canarytoken.value(), "updated@example.com")
        assert len(get_canarydrop(updated.canarytoken).triggered_details.hits) == 2
    finally:
        protocol.setTimeout(None)
        protocol.connectionLost(None)
