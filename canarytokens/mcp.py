from base64 import urlsafe_b64encode
from json import dumps
from random import choice
from os import urandom

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from canarytokens.models.mcp import McpAlertOn
from canarytokens.settings import FrontendSettings

settings = FrontendSettings()


def _base64url(data: bytes) -> str:
    return urlsafe_b64encode(data).rstrip(b"=").decode()


def _jwe_key() -> bytes:
    key = settings.MCP_SERVER_SECRET.encode()
    if len(key) != 16:
        raise ValueError("MCP_SERVER_SECRET must be 16 bytes for A128GCM")
    return key


def generate_jwe(string: str) -> str:
    protected = _base64url(
        dumps({"alg": "dir", "enc": "A128GCM"}, separators=(",", ":")).encode()
    )
    iv = urandom(12)
    encrypted = AESGCM(_jwe_key()).encrypt(iv, string.encode(), protected.encode())
    ciphertext, tag = encrypted[:-16], encrypted[-16:]
    return ".".join(
        [protected, "", _base64url(iv), _base64url(ciphertext), _base64url(tag)]
    )


def make_token_jwe(token_id: str, alert_on: McpAlertOn, aws_token: str = "") -> str:
    payload = {"token_id": token_id, "alert_on": alert_on.value, "aws_token": aws_token}
    return generate_jwe(dumps(payload))


def make_canary_mcp_json(
    token_id: str, alert_on: McpAlertOn, aws_token: str = ""
) -> str:
    config = {
        "mcpServers": {
            "cloud-auth-broker": {
                "type": "http",
                "url": choice(settings.MCP_SERVER_URLS),
                "headers": {
                    "Authorization": f"Bearer {make_token_jwe(token_id, alert_on, aws_token)}"
                },
            }
        }
    }
    return dumps(config, indent=2)
