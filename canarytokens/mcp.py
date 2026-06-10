from json import dumps
from jose import jwe

from canarytokens.settings import FrontendSettings

settings = FrontendSettings()

if settings.MCP_SERVER_URL:
    MCP_URL = settings.MCP_SERVER_URL
else:
    MCP_URL = ""

if settings.MCP_SERVER_SECRET:
    MCP_JWE_SECRET = settings.MCP_SERVER_SECRET
else:
    MCP_JWE_SECRET = "abcD0123defG4567"


def generate_jwe(string: str) -> str:
    return jwe.encrypt(
        string, MCP_JWE_SECRET, algorithm="dir", encryption="A128GCM"
    ).decode("utf-8")


def make_token_jwe(
    token_id: str, alert_on_connect: bool = False, aws_token: str = ""
) -> str:
    if alert_on_connect:
        alert = "connect"
    else:
        alert = "tool_call"
    payload = {"token_id": token_id, "alert_on": alert, "aws_token": aws_token}
    return generate_jwe(dumps(payload))


def make_canary_mcp_json(
    token_id: str, alert_on_connect: bool = False, aws_token: str = ""
) -> str:
    config = {
        "servers": {
            "cloud-auth-broker": {
                "type": "http",
                "url": MCP_URL,
                "headers": {
                    "Authorization": f"Bearer {make_token_jwe(token_id, alert_on_connect, aws_token)}"
                },
            }
        }
    }
    return dumps(config, indent=2)
