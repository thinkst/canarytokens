from typing import List, Literal, Optional

from canarytokens.utils import json_safe_dict
from .common import (
    DownloadContentTypes,
    DownloadFmtTypes,
    TokenDownloadRequest,
    TokenDownloadResponse,
    TokenHistory,
    TokenHit,
    TokenTypes,
)


class SlackAPITokenHit(TokenHit):
    token_type: Literal[TokenTypes.SLACK_API] = TokenTypes.SLACK_API
    additional_info: Optional[dict]

    def serialize_for_v2(self) -> dict:
        """Serialize an `AWSKeyTokenHit` into a dict
        that holds the equivalent info in the v2 shape.
        Returns:
            dict: AWSKeyTokenHit in v2 dict representation.
        """
        data = json_safe_dict(self, exclude=("token_type", "time_of_hit"))
        if "user_agent" in data:
            data["useragent"] = data.pop("user_agent")
        return data


class SlackAPITokenHistory(TokenHistory[SlackAPITokenHit]):
    token_type: Literal[TokenTypes.SLACK_API] = TokenTypes.SLACK_API
    hits: List[SlackAPITokenHit] = []


class DownloadSlackAPIRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.SLACK_API] = DownloadFmtTypes.SLACK_API


class DownloadSlackAPIResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    slack_api_key: str
    filename: str = "slack_creds"
    token: str
    auth: str
