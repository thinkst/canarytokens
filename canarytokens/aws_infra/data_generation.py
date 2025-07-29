from dataclasses import dataclass, field
from difflib import SequenceMatcher

import re
import json
import random

from canarytokens.aws_infra.utils import random_string
from canarytokens.models import AWSInfraAssetType
from canarytokens.settings import FrontendSettings
import httpx

import logging

log = logging.getLogger("DataGenerator")
log.setLevel(logging.INFO)

settings = FrontendSettings()

S3_BUCKET_NAME_REGEX = re.compile(
    r"^(?!\d{1,3}(\.\d{1,3}){3}$)[a-z0-9][a-z0-9\.\-]{1,61}[a-z0-9]$"
)
DYNAMO_DB_TABLE_NAME_REGEX = re.compile(r"[A-Za-z0-9_.\-]{3,255}")
SSM_PARAMETER_NAME_REGEX = re.compile(r"[A-Za-z0-9_.\-]+")
SQS_QUEUE_NAME_REGEX = re.compile(r"[A-Za-z0-9_\-;]{1,80}")
SECRETS_MANAGER_NAME_REGEX = re.compile(r"(?!.*\.\.)[A-Za-z0-9/_+=\.@\-]{1,512}")


async def make_request(
    url: str, method: str = "GET", headers: dict = None, data: dict = None
):
    """
    Generic HTTP request function using httpx.
    """
    REQUEST_TIMEOUT = 60  # seconds
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method, url, headers=headers, json=data, timeout=REQUEST_TIMEOUT
            )

            return response.status_code, response.content, response.headers
        except httpx.RequestError as e:
            raise RuntimeError(f"HTTP request failed: {e}")


@dataclass
class Suggestion:
    asset_type: AWSInfraAssetType
    suggested_names: list[str] = field(default_factory=list)


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
            "temperature": settings.GEMINI_TEMPERATURE,
            "response_mime_type": "application/json",
            "response_schema": {
                "required": ["suggested_names"],
                "properties": {
                    "suggested_names": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
                "type": "OBJECT",
            },
            "system_instruction": settings.GEMINI_SYSTEM_PROMPT,
        }
        self._MAX_ATTEMPTS = 5
        self._GEMINI_MODEL = settings.GEMINI_MODEL
        self._GEMINI_API_KEY = settings.GEMINI_API_KEY
        self._prompt_template = settings.GEMINI_PROMPT_TEMPLATE
        self._GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{self._GEMINI_MODEL}:generateContent"
        self._SIMILARITY_THRESHOLD = 0.9

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
        if count <= 0:
            raise ValueError("Count must be a positive integer.")

        while len(validated_names) < count:
            attempts += 1
            if attempts == self._MAX_ATTEMPTS:
                raise RuntimeError(
                    f"Failed to generate enough valid names for {asset_type.name} after {self._MAX_ATTEMPTS} attempts."
                )

            overshoot = max(count + 5, 2 * count - len(validated_names))
            new_names = await self._get_suggested_names(
                asset_type, inventory, count=overshoot
            )
            names = await self._finalize_list(asset_type, inventory, new_names, count)
            validated_names.extend(names)

        random.shuffle(validated_names)
        suggested_names = validated_names[:count]

        return Suggestion(asset_type, suggested_names)

    async def generate_children_names(
        self, parent_asset_type: AWSInfraAssetType, parent_name: str, count: int = 5
    ) -> list[str]:
        """
        Generate a list of child names for the specified AWS asset type.
        :param asset_type: The type of AWS asset to generate names for.
        :param inventory: A list of existing names for the specified asset type.
        :param count: The number of names to generate.
        :return: A list of generated child names.
        """
        if parent_asset_type not in [
            AWSInfraAssetType.S3_BUCKET,
            AWSInfraAssetType.DYNAMO_DB_TABLE,
        ]:
            raise ValueError(
                f"Child name generation is only supported for S3 buckets and DynamoDB tables, not {parent_asset_type.name}."
            )
        if parent_asset_type == AWSInfraAssetType.S3_BUCKET:
            child_description = (
                "objects (full paths including forward slashes are acceptable)"
            )
        else:
            child_description = "items"

        prompt = f"Generate {count} names for {child_description} in the {parent_asset_type.name} called {parent_name}."
        return await self._gemini_request(prompt)

    async def _validate_s3_name(self, name: str) -> bool:
        """Validate S3 bucket name asynchronously."""
        # Basic validation first
        if not (3 <= len(name) <= 63):
            return False
        if not re.match(S3_BUCKET_NAME_REGEX, name):
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
        return bool(re.fullmatch(DYNAMO_DB_TABLE_NAME_REGEX, name))

    def _validate_ssm_parameter_name(self, name: str) -> bool:
        # path segments of a-z A-Z 0-9 _ . - separated by "/"; no leading "aws" or "ssm"
        if not name or len(name) > 2048:
            return False
        segments = name.split("/")
        if segments[0].lower() in ("aws", "ssm"):
            return False
        for seg in segments:
            if not seg:
                continue  # skip empty segments
            if not re.fullmatch(SSM_PARAMETER_NAME_REGEX, seg):
                return False
        return True

    def _validate_sqs_name(self, name: str) -> bool:
        # 1-80 chars, A-Z a-z 0-9 _ - ;
        return bool(re.fullmatch(SQS_QUEUE_NAME_REGEX, name))

    def _validate_secrets_manager_name(self, name: str) -> bool:
        # 1-512 chars, A-Z a-z 0-9 / _ + = . @ - .
        return bool(re.fullmatch(SECRETS_MANAGER_NAME_REGEX, name))

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

    def _augment_name(self, asset_type: AWSInfraAssetType, name: str) -> str:
        """
        Augment a name with a random suffix to ensure uniqueness.
        """
        if asset_type == AWSInfraAssetType.S3_BUCKET:
            max_length = 63
            min_random_suffix_length = 3
            name = f"{name}-{random_string(random.randint(min_random_suffix_length, max_length // 3), lower_case_only=True)}"
            if len(name) > max_length:
                name = name[:max_length]

        return name

    async def _finalize_list(
        self,
        asset_type: AWSInfraAssetType,
        inventory: list[str],
        suggested_names: list[str],
        count: int,
    ) -> list[str]:
        """
        Get a list of validated names from the provided inventory.
        """
        validated_names = []
        for name in suggested_names:
            name = self._augment_name(asset_type, name)
            is_valid = await self._validate_name(asset_type, name)
            if (
                is_valid
                and self._similarity_score(name, inventory) < self._SIMILARITY_THRESHOLD
            ):
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

    async def _gemini_request(self, prompt: str):
        """
        Make a request to the Gemini API with the provided prompt.
        """
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
                try:
                    candidates = result.get("candidates")
                    if (
                        not candidates
                        or "content" not in candidates[0]
                        or "parts" not in candidates[0]["content"]
                    ):
                        log.error(
                            'Gemini API response missing expected keys: \'candidates[0]["content"]["parts"]\''
                        )
                        return []
                    parts = candidates[0]["content"]["parts"]
                    if not parts or "text" not in parts[0]:
                        log.error(
                            "Gemini API response missing expected key: 'text' in 'parts[0]'"
                        )
                        return []
                    parsed_content = json.loads(parts[0]["text"])
                    return parsed_content.get("suggested_names", [])

                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    log.error(f"Error parsing Gemini API response: {e}")
                    return []
            else:
                raise RuntimeError(f"Gemini API returned status {status_code}")

        except Exception as e:
            log.exception(f"Failed to get response from Gemini API: {e}")
            return []

    async def _get_suggested_names(
        self, asset_type: AWSInfraAssetType, inventory: list[str], count=5
    ):
        """
        Get suggested names from Gemini for the specified asset type based on the provided inventory.
        """
        prompt = self._prompt_template.format(
            count=count, service=asset_type.value, inventory=",".join(inventory)
        )

        return await self._gemini_request(prompt)
