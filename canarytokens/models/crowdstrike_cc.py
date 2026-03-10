from typing import Any, List, Literal, Optional, TypedDict

from pydantic import BaseModel, root_validator

from canarytokens.utils import json_safe_dict
from .common import (
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class CrowdStrikeCC(TypedDict):
    token_id: str
    client_id: str
    client_secret: str
    base_url: str


class CrowdStrikeCCAdditionalInfo(BaseModel):
    crowdstrike_log_data: dict[str, list[str]]

    @root_validator(pre=True)
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        keys_to_convert = [
            ("CrowdStrike Log Data", "crowdstrike_log_data"),
        ]
        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values:
                values[new_key] = values.pop(old_key)

        return {k.lower(): v for k, v in values.items()}

    def serialize_for_v2(self) -> dict:
        data = self.dict()
        keys_to_convert = [
            ("CrowdStrike Log Data", "crowdstrike_log_data"),
        ]
        for value, key in keys_to_convert:
            if key in data:
                data[value] = data.pop(key)
        return data


class CrowdStrikeCCTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CROWDSTRIKE_CC] = TokenTypes.CROWDSTRIKE_CC


class CrowdStrikeCCTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CROWDSTRIKE_CC] = TokenTypes.CROWDSTRIKE_CC
    client_id: str
    client_secret: str
    base_url: str


class CrowdStrikeCCTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CROWDSTRIKE_CC] = TokenTypes.CROWDSTRIKE_CC
    additional_info: Optional[CrowdStrikeCCAdditionalInfo]

    class Config:
        allow_population_by_field_name = True

    def serialize_for_v2(self) -> dict:
        data = json_safe_dict(self, exclude=("token_type", "time_of_hit"))
        if "additional_info" in data and self.additional_info:
            data["additional_info"] = self.additional_info.serialize_for_v2()
        if "user_agent" in data:
            data["useragent"] = data.pop("user_agent")
        return data


class CrowdStrikeCCTokenHistory(TokenHistory[CrowdStrikeCCTokenHit]):
    token_type: Literal[TokenTypes.CROWDSTRIKE_CC] = TokenTypes.CROWDSTRIKE_CC
    hits: List[CrowdStrikeCCTokenHit] = []
