from __future__ import absolute_import, print_function

import re
from datetime import datetime
from typing import Dict, List, Optional, Pattern, Tuple, TypedDict

from twisted.application import internet
from twisted.internet import defer
from twisted.logger import Logger
from twisted.mail import smtp
from twisted.mail.smtp import Address, User
from zope.interface import implementer

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import InputChannel
from canarytokens.constants import INPUT_CHANNEL_SMTP
from canarytokens.exceptions import NoCanarytokenFound, NoCanarydropFound
from canarytokens.models import (
    SMTPHeloField,
    SMTPMailField,
    SMTPTokenHistory,
    SMTPTokenHit,
    TokenTypes,
)
from canarytokens.queries import get_canarydrop, save_canarydrop
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

log = Logger()

MAX_HEADER_LINES = 1_000
MAX_HEADER_BYTES = 64 * 2**10
MAX_STORED_LINES = 10_000
MAX_STORED_BYTES = 5 * 2**20
MAX_ATTACHMENT_PARTS = 100
MAX_RECIPIENTS = 100  # Minimum recipient capacity as per RFC 5321, section 4.5.3.1.8.

# Store the original method before patching
original_lookup_method = smtp.ESMTP.lookupMethod


def patched_lookupMethod(self, command):
    """
    Patched version of lookupMethod that handles non-ASCII characters by closing the connection.
    """
    try:
        return original_lookup_method(self, command)
    except UnicodeDecodeError:
        # Log the issue and close the connection
        log.warn(
            f"Received command with non-ASCII characters from {self.transport.getPeer().host}: {command!r}"
        )
        self.sendLine(b"500 Syntax error, command unrecognized")
        self.transport.loseConnection()
        return None


# Apply the patch to the ESMTP class
smtp.ESMTP.lookupMethod = patched_lookupMethod


@implementer(smtp.IMessage)
class CanaryMessage:
    """Persist and dispatch hits using the drop bound during recipient validation."""

    def __init__(self, esmtp=None, *, canarydrop):
        self.esmtp = esmtp
        self.canarydrop = canarydrop
        self.headers = []
        self.headers_finished = False
        self.attachments = []
        self.links = []
        self.links_re: Pattern[bytes] = re.compile(rb"(http[s]?://[^\s'\"]+)", re.I)
        self.mime_boundary = None
        self.mime_boundary_re = re.compile(rb'.*boundary[ ]*=[" ]?([^" ]+)')
        self.in_mime_header = True
        self.lines = []
        self.stored_byte_count = 0
        self.header_byte_count = 0

    def lineReceived(self, line: bytes):
        """
        Reads each line of the SMTP message and parses it into,
        lines, attachments, headers etc.
        """
        if line == b"" and not self.headers_finished:
            self.headers_finished = True

        if not self.headers_finished:
            self._receive_header(line)
        else:
            if (
                len(self.lines) >= MAX_STORED_LINES
                or self.stored_byte_count >= MAX_STORED_BYTES
            ):
                return
            if self.mime_boundary:
                if self.in_mime_header:
                    if line == b"":
                        self.in_mime_header = False
                    elif self.attachments:
                        self.attachments[-1].append(line)

                if self.mime_boundary in line:
                    self.in_mime_header = True
                    if len(self.attachments) < MAX_ATTACHMENT_PARTS:
                        self.attachments.append([])

            self.lines.append(line)
            self.stored_byte_count += len(line)

    def _receive_header(self, line: bytes):
        if (
            len(self.headers) >= MAX_HEADER_LINES
            or self.header_byte_count >= MAX_HEADER_BYTES
        ):
            return
        self.headers.append(line)
        self.header_byte_count += len(line)
        m = self.mime_boundary_re.match(line)
        if m:
            self.mime_boundary = m.group(1)

    def eomReceived(self):
        """
        End of Message(eom) received. Create token hit and persist it to redis.
        """
        self.esmtp.mail["headers"] = self.headers
        self.esmtp.mail["links"] = self.links_re.findall(b"\r\n".join(self.lines))
        self.esmtp.mail["attachments"] = [b"\n".join(x) for x in self.attachments]

        log.info(
            f"New message received: {self.headers=}, {self.links=}, {self.attachments=}"
        )
        self.lines = None

        self.token_hit = SMTPTokenHit(
            time_of_hit=datetime.utcnow().strftime("%s.%f"),
            input_channel="SMTP",
            src_ip=self.esmtp.src_ip,
            geo_info=queries.get_geoinfo(ip=self.esmtp.src_ip),
            is_tor_relay=queries.is_tor_relay(ip=self.esmtp.src_ip),
            mail=SMTPMailField(
                recipients=[o.decode() for o in self.esmtp.mail["recipients"]],
                attachments=self.esmtp.mail["attachments"],
                sender=self.esmtp.mail["sender"],
                headers=self.esmtp.mail["headers"],
                links=self.esmtp.mail["links"],
                helo=SMTPHeloField(
                    client_name=self.esmtp.mail["helo"]["client_name"].decode(),
                    client_ip=self.esmtp.mail["helo"]["client_ip"].decode(),
                ),
            ),
        )
        self.canarydrop.add_canarydrop_hit(token_hit=self.token_hit)
        self.esmtp.dispatch(self.canarydrop, self.token_hit)

        d = defer.Deferred()
        d.callback("Success")
        return d

    def connectionLost(self):
        # There was an error, throw away the stored lines
        self.lines = None


class Mail(TypedDict):
    recipients: List[bytes]
    sender: List[bytes]
    helo: Dict[str, str]
    headers: List[bytes]
    links: List[bytes]
    attachments: List[bytes]


class CanaryESMTP(smtp.ESMTP):
    """Bound recipient-driven work within each SMTP transaction.

    Accept at most MAX_RECIPIENTS successful RCPT commands, including duplicates,
    but register only one delivery handler per token. Excess recipients receive
    452 so senders can retry them (RFC 5321 section 4.5.3.1).
    """

    def __init__(self, **kwargs):
        smtp.ESMTP.__init__(self, **kwargs)
        self.token_hit: Optional[SMTPTokenHit] = None
        self._recipient_count = 0
        self._recipient_tokens: set[str] = set()
        self.mail: Mail = {
            "recipients": [],
            "sender": "",
            "helo": {},
            "headers": [],
            "links": [],
            "attachments": [],
        }

    def greeting(
        self,
    ):
        self.src_ip = self.transport.getPeer().host
        try:
            return self.factory.responses["greeting"]
        except KeyError:
            return smtp.ESMTP.greeting(self)

    def receivedHeader(
        self, helo: Tuple[bytes, bytes], origin: Address, recipients: List[User]
    ):
        self.mail["helo"]["client_name"] = helo[0]
        self.mail["helo"]["client_ip"] = helo[1]
        self.mail["sender"] = str(origin)
        for r in recipients:
            address = r.dest.addrstr
            self.mail["recipients"].append(address)

    def validateFrom(self, helo: Tuple[bytes, bytes], origin: Address):
        self._reset_recipients()
        log.info(f"Got email from: {origin}")
        return origin

    def validateTo(self, user):
        if self._recipient_count >= MAX_RECIPIENTS:
            raise smtp.SMTPServerError(452, "Too many recipients")
        try:
            canarytoken = Canarytoken(value=user.dest.local)
            canarydrop = get_canarydrop(canarytoken=canarytoken)
            if canarydrop.type == TokenTypes.LEGACY:
                canarydrop.type = TokenTypes.SMTP
                canarydrop.triggered_details = SMTPTokenHistory(
                    hits=canarydrop.triggered_details.hits
                )
                save_canarydrop(canarydrop)
            return lambda: CanaryMessage(esmtp=self, canarydrop=canarydrop)
        except (NoCanarydropFound, NoCanarytokenFound):
            log.warn(
                "No token in recipient address: {address}".format(
                    address=user.dest.local
                )
            )
        except Exception as e:
            token = f" for {canarytoken.value()}" if canarytoken else ""
            log.error(f"Error in SMTP channel while validating To field{token}: {e}")

        raise smtp.SMTPBadRcpt(user)

    def _cbToValidate(self, to, user=None, code=250, msg=b"Recipient address accepted"):
        token = Canarytoken(value=user.dest.local).value()
        self._recipient_count += 1
        if token in self._recipient_tokens:
            self.sendCode(code, msg)
            return
        self._recipient_tokens.add(token)
        return super()._cbToValidate(to, user, code, msg)

    def _reset_recipients(self):
        self._recipient_count = 0
        self._recipient_tokens.clear()
        self.mail["recipients"].clear()

    def do_RSET(self, rest):
        self._reset_recipients()
        return super().do_RSET(rest)

    def _messageHandled(self, resultList):
        self._reset_recipients()
        return super()._messageHandled(resultList)

    def dispatch(
        self,
        canarydrop: Canarydrop,
        token_hit: SMTPTokenHit,
    ):
        self.factory.dispatch(canarydrop=canarydrop, token_hit=token_hit)


class CanarySMTPFactory(smtp.SMTPFactory, InputChannel):
    protocol = CanaryESMTP
    CHANNEL = INPUT_CHANNEL_SMTP

    def __init__(
        self,
        switchboard: Switchboard,
        frontend_settings: FrontendSettings,
        switchboard_settings: SwitchboardSettings,
    ):
        self.responses = {"data_success": b"Finished", "greeting": b"Hello there"}
        self.switchboard = switchboard
        # DESIGN: Ideally pass these in rather than have multiple inheritance
        smtp.SMTPFactory.__init__(self, portal=None)
        InputChannel.__init__(
            self,
            switchboard=self.switchboard,
            name=self.CHANNEL,
            unique_channel=False,
            switchboard_hostname=frontend_settings.DOMAINS[0],
            switchboard_scheme=switchboard_settings.SWITCHBOARD_SCHEME,
        )

    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
        #        p.delivery = self.delivery
        #        p.challengers = {"LOGIN": LOGINCredentials, "PLAIN": PLAINCredentials}
        return p


class ChannelSMTP:
    def __init__(
        self,
        frontend_settings: FrontendSettings,
        switchboard_settings: SwitchboardSettings,
        switchboard: Switchboard,
    ):
        self.service = internet.TCPServer(
            switchboard_settings.CHANNEL_SMTP_PORT,
            CanarySMTPFactory(
                switchboard=switchboard,
                frontend_settings=frontend_settings,
                switchboard_settings=switchboard_settings,
            ),
        )
