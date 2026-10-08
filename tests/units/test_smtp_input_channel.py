from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from twisted.internet.testing import StringTransport
from twisted.mail.smtp import Address, User

from canarytokens.canarydrop import Canarydrop
from canarytokens.channel_input_smtp import (
    MAX_ATTACHMENT_PARTS,
    MAX_HEADER_BYTES,
    MAX_HEADER_LINES,
    MAX_STORED_BYTES,
    MAX_STORED_LINES,
    CanaryESMTP,
    CanaryMessage,
    CanarySMTPFactory,
)
from canarytokens.models import TokenTypes
from canarytokens.queries import save_canarydrop
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken
from tests.utils import slack_webhook_test

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

    cm = CanaryMessage(esmtp=None)
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
    cm = CanaryMessage(esmtp=None)
    line = b"X-Pad: " + b"B" * 16300
    for _ in range(100):
        cm.lineReceived(line)
    assert cm.header_byte_count >= MAX_HEADER_BYTES
    assert cm.header_byte_count < MAX_HEADER_BYTES + len(line)
    assert len(cm.headers) * (len(line) + 1) < 5 * 2**20


def test_header_flood_bounded_by_line_count():
    cm = CanaryMessage(esmtp=None)
    for _ in range(MAX_HEADER_LINES * 2):
        cm.lineReceived(b"X")
    assert len(cm.headers) == MAX_HEADER_LINES


def test_boundary_flood_bounded():
    cm = CanaryMessage(esmtp=None)
    cm.lineReceived(b"Content-Type: multipart/mixed; boundary=b")
    cm.lineReceived(b"")
    for _ in range(100_000):
        cm.lineReceived(b"b")
    assert len(cm.attachments) == MAX_ATTACHMENT_PARTS
    assert len(cm.lines) == MAX_STORED_LINES
    assert sum(len(a) for a in cm.attachments) <= MAX_STORED_LINES


def test_links_survive_header_flood():
    cm = CanaryMessage(esmtp=None)
    for _ in range(500):
        cm.lineReceived(b"X-Pad: " + b"B" * 16300)
    cm.lineReceived(b"")
    cm.lineReceived(b"visit https://evil.example/abc now")
    links = cm.links_re.findall(b"\r\n".join(cm.lines))
    assert b"https://evil.example/abc" in links


def test_body_flood_bounded_by_bytes():
    cm = CanaryMessage(esmtp=None)
    cm.lineReceived(b"Subject: x")
    cm.lineReceived(b"")
    line = b"B" * 1000
    for _ in range(MAX_STORED_LINES * 2):
        cm.lineReceived(line)
    assert cm.stored_byte_count >= MAX_STORED_BYTES
    assert cm.stored_byte_count < MAX_STORED_BYTES + len(line)
    assert len(cm.lines) < MAX_STORED_LINES


def test_body_flood_bounded_by_line_count():
    cm = CanaryMessage(esmtp=None)
    cm.lineReceived(b"Subject: x")
    cm.lineReceived(b"")
    for _ in range(MAX_STORED_LINES * 2):
        cm.lineReceived(b"B")
    assert len(cm.lines) == MAX_STORED_LINES
    assert cm.stored_byte_count <= MAX_STORED_LINES


def test_normal_mail_still_parsed():
    cm = CanaryMessage(esmtp=None)
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
