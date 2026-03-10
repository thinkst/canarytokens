from typing import Any, List, Literal, Optional
from .common import (
    BaseModel,
    Field,
    TokenExposedHit,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
    json_safe_dict,
    root_validator,
    strtobool,
)


class AWSKeyAdditionalInfo(BaseModel):
    aws_key_log_data: dict[str, list[str]]

    @root_validator(pre=True)
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        keys_to_convert = [
            # TODO: make this consistent.
            ("AWS Key Log Data", "aws_key_log_data"),
        ]
        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values:
                values[new_key] = values.pop(old_key)

        return {k.lower(): v for k, v in values.items()}


class AWSKeyTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS


class AWSKeyTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    output: str


class AWSKeyTokenHit(TokenHit):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    useragent: Optional[str] = Field(
        None, alias="user_agent"
    )  # V2 does / did not store user agent.
    additional_info: Optional[AWSKeyAdditionalInfo]

    class Config:
        allow_population_by_field_name = True

    @property
    def safety_net(self):
        if self.additional_info is None:
            return False
        if safety_net := self.additional_info.aws_key_log_data.get("safety_net", False):
            if isinstance(safety_net, list):
                return strtobool(safety_net[0])
        return False

    @property
    def service_used(self):
        if self.additional_info is None:
            return False
        if service_used := self.additional_info.aws_key_log_data.get(
            "service_used", False
        ):
            if isinstance(service_used, list):
                return service_used[0]
            else:
                return service_used
        return False

    def serialize_for_v2(self) -> dict:
        """Serialize an `AWSKeyTokenHit` into a dict
        that holds the equivalent info in the v2 shape.
        Returns:
            dict: AWSKeyTokenHit in v2 dict representation.
        """
        data = json_safe_dict(self, exclude=("token_type", "time_of_hit"))
        if "additional_info" in data and "aws_key_log_data" in data["additional_info"]:
            data["additional_info"]["AWS Key Log Data"] = data["additional_info"].pop(
                "aws_key_log_data"
            )
        if "user_agent" in data:
            data["useragent"] = data.pop("user_agent")
        return data

    def __init__(__pydantic_self__, **data):
        # Only for V2 compatibility.
        if not data.get("geo_info", False):
            data["geo_info"] = ""
        if not data.get("is_tor_relay", False):
            data["is_tor_relay"] = False
        if data.get("safety_net", False):
            additional_info = data.get("additional_info", {})
            log_data = additional_info.get("AWS Key Log Data", {})
            log_data.update(
                {
                    "safety_net": [str(data["safety_net"])],
                    "service_used": [str(data["service_used"])],
                }
            )
            data["additional_info"] = {"AWS Key Log Data": log_data}
        super().__init__(**data)

    @root_validator(allow_reuse=True)
    def validate_extras(cls, values):
        dependent_vals = [
            # "src_ip", #V2 stores src_ip as "". It's not None.
            # "geo_info",  #V2 stores geo info as "" on some hits.
            # "is_tor_relay", #V2 stores `is_tor_relay` on some hits even if src_ip is not there.
            # "user_agent", #V2 Does not store user agent for all hits
            # "additional_info", #V2 stores empty additional data. It's not None.
        ]

        if values.get("safety_net", False) or not values.get("src_ip", False):
            for x in dependent_vals:
                if values.get(x, None) is not None:
                    raise TypeError(f"{x} should be None when safety_net=True")
        else:
            for x in dependent_vals:
                if values.get(x, None) is None:
                    raise TypeError(f"{x} should not be None when safety_net=False")
        return values


class AWSKeyTokenExposedHit(TokenExposedHit):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    public_location: Optional[str]
    input_channel: str = "HTTP"


class AWSKeyTokenHistory(TokenHistory[AWSKeyTokenHit]):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    hits: List[AWSKeyTokenHit]
