from typing import Any, List, Literal, Optional

from pydantic import root_validator

from canarytokens.utils import json_safe_dict
from .common import (
    BaseModel,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class AzureIDAdditionalInfo(BaseModel):
    azure_id_log_data: dict[str, list[str]]
    microsoft_azure: dict[str, list[str]]
    location: dict[str, list[str]]
    coordinates: dict[str, list[str]]

    @root_validator(pre=True)
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        keys_to_convert = [
            # TODO: make this consistent.
            ("Azure ID Log Data", "azure_id_log_data"),
            ("Microsoft Azure", "microsoft_azure"),
            ("Location", "location"),
            ("Coordinates", "coordinates"),
        ]
        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values:
                values[new_key] = values.pop(old_key)

        return {k.lower(): v for k, v in values.items()}

    def serialize_for_v2(self) -> dict:
        """Serialize an `AzureIDTokenHit` into a dict
        that holds the equivalent info in the v2 shape.
        Returns:
            dict: AzureIDTokenHit in v2 dict representation.
        """
        data = self.dict()
        keys_to_convert = [
            # TODO: make this consistent.
            ("Azure ID Log Data", "azure_id_log_data"),
            ("Microsoft Azure", "microsoft_azure"),
            ("Location", "location"),
            ("Coordinates", "coordinates"),
        ]
        for value, key in keys_to_convert:
            if key in data:
                data[value] = data.pop(key)
        return data


class AzureIDTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.AZURE_ID] = TokenTypes.AZURE_ID
    azure_id_cert_file_name: str


class AzureIDTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.AZURE_ID] = TokenTypes.AZURE_ID
    app_id: str
    tenant_id: str
    cert: str
    cert_name: str
    cert_file_name: str


class AzureIDTokenHit(TokenHit):
    token_type: Literal[TokenTypes.AZURE_ID] = TokenTypes.AZURE_ID
    additional_info: Optional[AzureIDAdditionalInfo]

    class Config:
        allow_population_by_field_name = True

    def serialize_for_v2(self) -> dict:
        """Serialize an `AzureIDTokenHit` into a dict
        that holds the equivalent info in the v2 shape.
        Returns:
            dict: AzureIDTokenHit in v2 dict representation.
        """
        data = json_safe_dict(self, exclude=("token_type", "time_of_hit"))
        if "additional_info" in data:
            data["additional_info"] = self.additional_info.serialize_for_v2()
        return data


class AzureIDTokenHistory(TokenHistory):
    token_type: Literal[TokenTypes.AZURE_ID] = TokenTypes.AZURE_ID
    hits: List[AzureIDTokenHit]
