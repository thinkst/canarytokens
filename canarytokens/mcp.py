from json import dumps
from jose import jwe
from random import choice

from canarytokens.models.mcp import McpAlertOn
from canarytokens.settings import FrontendSettings

settings = FrontendSettings()


def generate_jwe(string: str) -> str:
    return jwe.encrypt(
        string, settings.MCP_SERVER_SECRET, algorithm="dir", encryption="A128GCM"
    ).decode()


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
