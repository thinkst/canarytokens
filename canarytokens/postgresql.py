import hashlib
import os
import struct

from twisted.internet.protocol import Factory, Protocol
from twisted.logger import Logger

log = Logger()

PROTOCOL_VERSION = 196608  # 3.0
SSL_REQUEST_CODE = 80877103
CANCEL_REQUEST_CODE = 80877102

AUTH_OK = 0
AUTH_MD5_PASSWORD = 5

MSG_AUTH = ord("R")
MSG_ERROR_RESPONSE = ord("E")
MSG_PASSWORD = ord("p")


def md5_hex(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def compute_md5_inner_hash(password: str, username: str) -> str:
    """md5(password + username) - stored as lookup key at creation time."""
    return md5_hex((password + username).encode("utf-8"))


def compute_md5_response(inner_hash: str, salt: bytes) -> str:
    """Full PG MD5 response: 'md5' + md5(inner_hash + salt)."""
    return "md5" + md5_hex(inner_hash.encode("utf-8") + salt)


class PostgreSQLProtocol(Protocol):

    def __init__(self, channel):
        self.channel = channel
        self._buffer = b""
        self._state = "startup"
        self._username = ""
        self._database = ""
        self._salt = b""
        self._client_params = {}

    def dataReceived(self, data: bytes):
        self._buffer += data
        try:
            self._process()
        except Exception:
            log.failure("PostgreSQL protocol error")
            self.transport.loseConnection()

    def _process(self):
        while self._buffer:
            if self._state == "startup":
                if not self._handle_startup():
                    return
            elif self._state == "wait_password":
                if not self._handle_password():
                    return
            else:
                return

    def _handle_startup(self) -> bool:
        if len(self._buffer) < 4:
            return False

        msg_len = struct.unpack("!I", self._buffer[:4])[0]
        if len(self._buffer) < msg_len:
            return False

        packet = self._buffer[:msg_len]
        self._buffer = self._buffer[msg_len:]

        if msg_len < 8:
            self.transport.loseConnection()
            return False

        code = struct.unpack("!I", packet[4:8])[0]

        if code == SSL_REQUEST_CODE:
            self.transport.write(b"N")
            return True

        if code == CANCEL_REQUEST_CODE:
            self.transport.loseConnection()
            return False

        if code == PROTOCOL_VERSION:
            self._parse_params(packet[8:])
            self._send_md5_challenge()
            self._state = "wait_password"
            return True

        self._send_error("08P01", "unsupported protocol version")
        self.transport.loseConnection()
        return False

    def _parse_params(self, data: bytes):
        params = {}
        while len(data) > 1:
            idx = data.find(b"\x00")
            if idx < 0:
                break
            key = data[:idx].decode("utf-8", errors="replace")
            data = data[idx + 1 :]
            idx = data.find(b"\x00")
            if idx < 0:
                break
            params[key] = data[:idx].decode("utf-8", errors="replace")
            data = data[idx + 1 :]
        self._username = params.get("user", "")
        self._database = params.get("database", self._username)
        self._client_params = {
            k: v for k, v in params.items() if k not in ("user", "database")
        }

    def _send_md5_challenge(self):
        self._salt = os.urandom(4)
        buf = bytearray(13)
        buf[0] = MSG_AUTH
        struct.pack_into("!I", buf, 1, 12)
        struct.pack_into("!I", buf, 5, AUTH_MD5_PASSWORD)
        buf[9:13] = self._salt
        self.transport.write(bytes(buf))

    def _handle_password(self) -> bool:
        if len(self._buffer) < 5:
            return False

        if self._buffer[0] != MSG_PASSWORD:
            self.transport.loseConnection()
            return False

        msg_len = struct.unpack("!I", self._buffer[1:5])[0]
        total = 1 + msg_len
        if len(self._buffer) < total:
            return False

        payload = self._buffer[5:total]
        self._buffer = self._buffer[total:]
        if payload and payload[-1:] == b"\x00":
            payload = payload[:-1]

        client_hash = payload.decode("utf-8", errors="replace")
        self._state = "done"

        self.channel.handle_auth(
            protocol=self,
            username=self._username,
            database=self._database,
            client_hash=client_hash,
            salt=self._salt,
            src_ip=self.transport.getPeer().host,
            client_params=self._client_params,
        )
        return True

    def _send_error(self, code: str, message: str):
        payload = bytearray()
        for field_type, value in [
            ("S", "ERROR"),
            ("V", "ERROR"),
            ("C", code),
            ("M", message),
        ]:
            payload.append(ord(field_type))
            payload.extend(value.encode("utf-8"))
            payload.append(0)
        payload.append(0)

        buf = bytearray(1 + 4 + len(payload))
        buf[0] = MSG_ERROR_RESPONSE
        struct.pack_into("!I", buf, 1, 4 + len(payload))
        buf[5:] = payload
        self.transport.write(bytes(buf))

    def deny(self):
        self._send_error(
            "28P01", f'password authentication failed for user "{self._username}"'
        )
        self.transport.loseConnection()


class PostgreSQLFactory(Factory):
    def __init__(self, channel):
        self.channel = channel

    def buildProtocol(self, addr):
        return PostgreSQLProtocol(channel=self.channel)
