from typing import List, Literal, Optional
from .common import TokenHistory, TokenHit, TokenTypes, json_safe_dict


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
