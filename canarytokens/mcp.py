from json import dumps
from jose import jwe

from canarytokens.models.mcp import McpAlertOn
from canarytokens.settings import FrontendSettings

settings = FrontendSettings()

MCP_URL = settings.MCP_SERVER_URL
MCP_JWE_SECRET = settings.MCP_SERVER_SECRET


def generate_jwe(string: str) -> str:
    return jwe.encrypt(
        string, MCP_JWE_SECRET, algorithm="dir", encryption="A128GCM"
    ).decode("utf-8")


def make_token_jwe(token_id: str, alert_on: McpAlertOn, aws_token: str = "") -> str:
    payload = {"token_id": token_id, "alert_on": alert_on.value, "aws_token": aws_token}
    return generate_jwe(dumps(payload))


def make_canary_mcp_json(
    token_id: str, alert_on: McpAlertOn, aws_token: str = ""
) -> str:
    config = {
        "servers": {
            "cloud-auth-broker": {
                "type": "http",
                "url": MCP_URL,
                "headers": {
                    "Authorization": f"Bearer {make_token_jwe(token_id, alert_on, aws_token)}"
                },
            }
        }
    }
    return dumps(config, indent=2)
