from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import List

import re
import json
import random

from canarytokens.models import AWSInfraAssetType
from canarytokens.settings import FrontendSettings
import httpx

import logging

log = logging.getLogger("DataGenerator")
log.setLevel(logging.INFO)

settings = FrontendSettings()


def _get_system_prompt():
    return settings.GEMINI_SYSTEM_PROMPT


async def make_request(
    url: str, method: str = "GET", headers: dict = None, data: dict = None
):
    """
    Generic HTTP request function using httpx.
    """
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "POST":
                response = await client.post(
                    url, json=data, headers=headers, timeout=60
                )
            elif method.upper() == "HEAD":
                response = await client.head(url, headers=headers)
            elif method.upper() == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.request(method, url, headers=headers, json=data)

            return response.status_code, response.content, response.headers
        except httpx.RequestError as e:
            raise RuntimeError(f"HTTP request failed: {e}")


@dataclass
class Suggestion:
    asset_type: AWSInfraAssetType
    suggested_names: List[str] = field(default_factory=list)


class GeminiDecoyNameGenerator:
    def __init__(self):
        self._validator_map = {
            AWSInfraAssetType.S3_BUCKET: self._validate_s3_name,
            AWSInfraAssetType.DYNAMO_DB_TABLE: self._validate_dynamodb_name,
            AWSInfraAssetType.SSM_PARAMETER: self._validate_ssm_parameter_name,
            AWSInfraAssetType.SQS_QUEUE: self._validate_sqs_name,
            AWSInfraAssetType.SECRETS_MANAGER_SECRET: self._validate_secrets_manager_name,
        }
        self._gemini_config = {
            "temperature": 1.8,
            "response_mime_type": "application/json",
            "response_schema": {
                "required": ["suggested_names"],
                "properties": {
                    "suggested_names": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
                "type": "OBJECT",
            },
            "system_instruction": _get_system_prompt(),
        }
        self._max_attempts = 5
        self._GEMINI_MODEL = "gemini-2.5-flash"
        self._GEMINI_API_KEY = settings.GEMINI_API_KEY
        self._prompt_template = "In line with your system instructions, generate a list of {count} decoy asset names for the following AWS service based on the provided inventory. If the list for the service type in the provided inventory is empty, still return a list of {count} names.\n{service} inventory names found: [{inventory}]"
        self._GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{self._GEMINI_MODEL}:generateContent"

    async def generate_names(
        self, asset_type: AWSInfraAssetType, inventory: list[str], count=5
    ) -> Suggestion:
        """
        Generate decoy names for the specified AWS asset type based on the provided inventory.
        :param asset_type: The type of AWS asset to generate names for.
        :param inventory: A list of existing names foar the specified asset type.
        :param count: The number of names to generate.
        :return: A Suggestion object containing the generated names.
        """
        validated_names = []
        attempts = 0

        while len(validated_names) < count:
            attempts += 1
            if attempts == self._max_attempts:
                raise RuntimeError(
                    f"Failed to generate enough valid names for {asset_type.name} after {self._max_attempts} attempts."
                )

            overshoot = max(count + 5, 2 * count - len(validated_names))
            new_names = await self._get_suggested_names(
                asset_type, inventory, count=overshoot
            )
            trimmed_names = await self._trim_list(
                asset_type, inventory, new_names, count
            )
            validated_names.extend(trimmed_names)

        random.shuffle(validated_names)
        suggested_names = validated_names[:count]

        return Suggestion(asset_type, suggested_names)

    async def _validate_s3_name(self, name: str) -> bool:
        """Validate S3 bucket name asynchronously."""
        # Basic validation first
        if not (3 <= len(name) <= 63):
            return False
        if not re.match(r"^[a-z0-9][a-z0-9\.\-]{1,61}[a-z0-9]$", name):
            return False
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", name):  # IP-style
            return False

        reserved_prefixes = (
            "xn--",
            "sthree-",
            "sthree-configurator",
            "s3alias",
            "s3-",
            "s3control-",
        )
        reserved_suffixes = ("--ol-s3",)
        if any(name.startswith(p) for p in reserved_prefixes) or any(
            name.endswith(s) for s in reserved_suffixes
        ):
            return False

        # Check if bucket exists using async HTTP request
        url = f"https://{name}.s3.amazonaws.com"
        try:
            status_code, _, _ = await make_request(url, method="HEAD")
            bucket_exists = status_code in (200, 403) and status_code != 404
        except Exception:
            log.exception("Error checking S3 bucket existence")
            return False

        if not bucket_exists:
            return True

        return False

    def _validate_dynamodb_name(self, name: str) -> bool:
        # 3-255 chars, A-Z a-z 0-9 _ - .
        return bool(re.fullmatch(r"[A-Za-z0-9_.\-]{3,255}", name))

    def _validate_ssm_parameter_name(self, name: str) -> bool:
        # path segments of a-z A-Z 0-9 _ . - separated by "/"; no leading "aws" or "ssm"
        if not name or name.startswith("/") or len(name) > 2048:
            return False
        segments = name.split("/")
        if segments[0].lower() in ("aws", "ssm"):
            return False
        for seg in segments:
            if not re.fullmatch(r"[A-Za-z0-9_.\-]+", seg):
                return False
        return True

    def _validate_sqs_name(self, name: str) -> bool:
        # 1-80 chars, A-Z a-z 0-9 _ - ;
        return bool(re.fullmatch(r"[A-Za-z0-9_\-;]{1,80}", name))

    def _validate_secrets_manager_name(self, name: str) -> bool:
        # 1-512 chars, A-Z a-z 0-9 / _ + = . @ - .
        return bool(re.fullmatch(r"[A-Za-z0-9/_+=\.@\-]{1,512}", name))

    async def _validate_name(self, asset_type: AWSInfraAssetType, name: str) -> bool:
        """
        Validate a name against the rules for the specified AWS asset type.
        """
        validator = self._validator_map.get(asset_type)
        if not validator:
            raise ValueError(f"No validator found for asset type {asset_type.name}.")

        # Handle async validators (like S3) vs sync validators
        if asset_type == AWSInfraAssetType.S3_BUCKET:
            return await validator(name)
        else:
            return validator(name)

    def _similarity_score(self, name, inventory):
        return max(
            (SequenceMatcher(None, name, existing).ratio() for existing in inventory),
            default=0,
        )

    async def _trim_list(
        self,
        asset_type: AWSInfraAssetType,
        inventory: list[str],
        suggested_names: list[str],
        count: int,
    ) -> list[str]:
        """
        Get a list of validated names from the provided inventory.
        """
        assert count > 0, "Count must be a positive integer."

        validated_names = []
        for name in suggested_names:
            is_valid = await self._validate_name(asset_type, name)
            if is_valid and not self._similarity_score(name, inventory) >= 0.9:
                validated_names.append(name)

        return validated_names

    def _get_post_data(self, prompt: str):
        return {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self._gemini_config["temperature"],
                "responseMimeType": self._gemini_config["response_mime_type"],
                "responseSchema": self._gemini_config["response_schema"],
            },
            "systemInstruction": {
                "parts": [{"text": self._gemini_config["system_instruction"]}]
            },
        }

    async def _get_suggested_names(
        self, asset_type: AWSInfraAssetType, inventory: list[str], count=5
    ):
        """
        Get suggested names from Gemini for the specified asset type based on the provided inventory.
        """
        assert count > 0, "Count must be a positive integer."

        prompt = self._prompt_template.format(
            count=count, service=asset_type.value, inventory=",".join(inventory)
        )

        log.info(
            f"Generating {count} names for {asset_type.value} with prompt: {prompt}"
        )

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self._GEMINI_API_KEY,
        }

        try:
            status_code, response_body, _ = await make_request(
                self._GEMINI_API_URL,
                method="POST",
                headers=headers,
                data=self._get_post_data(prompt),
            )

            if status_code == 200:
                result = json.loads(response_body.decode("utf-8"))
                parsed_content = json.loads(
                    result["candidates"][0]["content"]["parts"][0]["text"]
                )
                return parsed_content.get("suggested_names", [])
            else:
                raise RuntimeError(f"Gemini API returned status {status_code}")

        except Exception as e:
            log.exception(f"Failed to get response from Gemini API: {e}")
            return []
