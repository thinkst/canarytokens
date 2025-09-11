import asyncio
import json
import logging
import random
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from functools import cached_property

import httpx

from canarytokens.aws_infra.db_queries import (
    get_data_generation_requests,
    update_data_generation_requests,
)
from canarytokens.aws_infra.utils import (
    AssetNameValidation,
    generate_s3_bucket_suffix,
    s3_bucket_is_available,
    validate_dynamodb_name,
    validate_s3_name,
    validate_secrets_manager_name,
    validate_sqs_name,
    validate_ssm_parameter_name,
)
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetType
from canarytokens.settings import FrontendSettings


log = logging.getLogger("DataGenerator")
log.setLevel(logging.INFO)

settings = FrontendSettings()

_GEMINI_CONFIG = {
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

_NAME_GEN_MAX_ATTEMPTS = 5
_GEMINI_MODEL = settings.GEMINI_MODEL
_GEMINI_API_KEY = settings.GEMINI_API_KEY
_prompt_template = settings.GEMINI_PROMPT_TEMPLATE
_GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_MODEL}:generateContent"
_SIMILARITY_THRESHOLD = 0.9


@dataclass
class _Suggestion:
    asset_type: AWSInfraAssetType
    suggested_names: list[str] = field(default_factory=list)


def _httpx_async_client_default():
    return httpx.AsyncClient(timeout=60)


async def _validate_s3_name_and_availability(name: str) -> AssetNameValidation:
    """
    Validate an S3 bucket name and check its availability.
    """
    is_valid = validate_s3_name(name).result
    if not is_valid:
        return AssetNameValidation(
            result=False, error_message=f"Invalid S3 bucket name: {name}"
        )

    if not await s3_bucket_is_available(name):
        return AssetNameValidation(
            result=False, error_message=f"S3 bucket does not exist: {name}"
        )

    return AssetNameValidation(result=True)


_VALIDATORS = {
    AWSInfraAssetType.S3_BUCKET: _validate_s3_name_and_availability,
    AWSInfraAssetType.DYNAMO_DB_TABLE: validate_dynamodb_name,
    AWSInfraAssetType.SSM_PARAMETER: validate_ssm_parameter_name,
    AWSInfraAssetType.SQS_QUEUE: validate_sqs_name,
    AWSInfraAssetType.SECRETS_MANAGER_SECRET: validate_secrets_manager_name,
}


async def _validate_name(asset_type: AWSInfraAssetType, name: str) -> bool:
    """
    Validate a name against the rules for the specified AWS asset type.
    """
    validator = _VALIDATORS.get(asset_type)
    if not validator:
        raise ValueError(f"No validator found for asset type {asset_type.name}.")

    # Handle async validators (like S3) vs sync validators
    if asset_type == AWSInfraAssetType.S3_BUCKET:
        return (await validator(name)).result
    else:
        return validator(name).result


def _augment_s3_bucket_name(name: str) -> str:
    """
    Augment a name with a random suffix to ensure uniqueness.
    """
    max_length = 63
    name = f"{name}-{generate_s3_bucket_suffix()}"
    if len(name) > max_length:
        name = name[:max_length]

    return name


async def _finalize_list(
    asset_type: AWSInfraAssetType,
    inventory: list[str],
    suggested_names: list[str],
) -> list[str]:
    """
    Get a list of validated names from the provided inventory.
    """
    validated_names = []
    is_valid_tasks = []
    asset_names = []

    if asset_type == AWSInfraAssetType.S3_BUCKET:
        suggested_names = list(map(_augment_s3_bucket_name, suggested_names))

    for name in suggested_names:
        is_valid_tasks.append(_validate_name(asset_type, name))
        asset_names.append(name)

    is_valid_results = await asyncio.gather(*is_valid_tasks)
    for name, is_valid in zip(asset_names, is_valid_results):
        if not is_valid:
            continue
        similarity_score = max(
            (SequenceMatcher(None, name, existing).ratio() for existing in inventory),
            default=0,
        )

        if similarity_score < _SIMILARITY_THRESHOLD:
            validated_names.append(name)
    return validated_names


async def _gemini_request(prompt: str):
    """
    Make a request to the Gemini API with the provided prompt.
    """
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": _GEMINI_API_KEY,
    }

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": _GEMINI_CONFIG["temperature"],
            "responseMimeType": _GEMINI_CONFIG["response_mime_type"],
            "responseSchema": _GEMINI_CONFIG["response_schema"],
        },
        "systemInstruction": {
            "parts": [{"text": _GEMINI_CONFIG["system_instruction"]}]
        },
    }

    try:
        async with _httpx_async_client_default() as client:
            response = await client.post(_GEMINI_API_URL, headers=headers, json=data)

        if response.status_code != 200:
            raise RuntimeError(f"Gemini API returned status {response.status_code}")

        result = json.loads(response.content.decode("utf-8"))
        parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])
        text = parts[0].get("text", "")
        if not text:
            log.error(
                'No text found in Gemini API response, missing: ["candidates"][0]["content"]["parts"][0]["text"]'
            )
            return []

        parsed_content = json.loads(text)
        return parsed_content.get("suggested_names", [])

    except json.JSONDecodeError:
        log.exception("Error parsing Gemini API response.")
    except Exception:
        log.exception("Failed to get response from Gemini API.")

    return []


def _overshoot_count(count: int, validated_count: int = 0) -> int:
    """
    Calculate the overshoot count based on the provided count.
    :param count: The number of names to generate.
    :param validated_count: The number of already validated names.
    :return: The overshoot count.
    """
    if count <= 0:
        raise ValueError("Count must be a positive integer.")
    return max(count + 5, 2 * count - validated_count)


async def generate_names(
    asset_type: AWSInfraAssetType, inventory: list[str], count=5, trim_list: bool = True
) -> _Suggestion:
    """
    Generate decoy names for the specified AWS asset type based on the provided inventory.
    :param asset_type: The type of AWS asset to generate names for.
    :param inventory: A list of existing names for the specified asset type.
    :param count: The number of names to generate.
    :return: A Suggestion object containing the generated names.
    """
    if inventory is None:
        # if inventory is None, we assume we don't have permissions to inventory, return empty suggestion
        return _Suggestion(asset_type, [])

    validated_names = []
    attempts = 0
    if count <= 0:
        raise ValueError("Count must be a positive integer.")

    while len(validated_names) < count:
        attempts += 1
        if attempts == _NAME_GEN_MAX_ATTEMPTS:
            raise RuntimeError(
                f"Failed to generate enough valid names for {asset_type.name} after {_NAME_GEN_MAX_ATTEMPTS} attempts."
            )

        # Use a heuristic to calculate how many suggestions to ask for
        #
        # At the time of writing, only a few of the names Gemini generates
        # are invalid. The heuristic aims to minimise the cost using Gemini
        # which is based on both the number of input tokens sent, and output
        # tokens received (with output being ~8x input). The heuristic here was
        # chosen by playing around with the API trying to minimise the number
        # of queries sent and the size of the result needed for enough valid names.
        #
        new_names = await _gemini_request(
            prompt=_prompt_template.format(
                count=_overshoot_count(count, len(validated_names)),
                service=asset_type.value,
                inventory=",".join(inventory),
            )
        )
        names = await _finalize_list(asset_type, inventory, new_names)
        validated_names.extend(names)

    random.shuffle(validated_names)
    suggested_names = validated_names[:count] if trim_list else validated_names

    return _Suggestion(asset_type, suggested_names)


async def generate_children_names(
    parent_asset_type: AWSInfraAssetType,
    parent_name: str,
    count: int = 5,
    trim_list: bool = True,
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

    result = await _gemini_request(
        prompt=f"Generate {_overshoot_count(count)} names for {child_description} in the {parent_asset_type.name} called {parent_name}."
    )
    return result[:count] if trim_list else result


@dataclass(frozen=True)
class _NameGenerationLimitUsage:
    count: int

    @cached_property
    def remaining(self) -> int:
        return max(settings.AWS_INFRA_NAME_GENERATION_LIMIT - self.count, 0)


def name_generation_limit_usage(canarydrop: Canarydrop) -> _NameGenerationLimitUsage:
    """
    Get the Gemini usage statistics for the canarydrop.
    :param canarydrop: The canarydrop instance for which to retrieve usage statistics.
    :return: An object containing the usage statistics.
    """
    return _NameGenerationLimitUsage(count=get_data_generation_requests(canarydrop))


def name_generation_usage_consume(canarydrop: Canarydrop, count: int = 1) -> None:
    """
    Increment the Gemini usage count for the canarydrop and persist the change by calling canarydrop.save().
    :param canarydrop: The canarydrop instance for which to increment usage.
    :param value: The amount to increment the usage by (default is 1).
    :return: None
    """
    if count <= 0:
        raise ValueError("Count must be a positive integer.")

    if not name_generation_limit_usage(canarydrop).remaining:
        log.warning(
            f"Canarytoken {canarydrop.canarytoken.value()} has already reached the Gemini data generation limit."
        )
        return
    # The first request to exceed the limit is always allowed regardless of the count to consume.
    # Later tries over the limit will always be rejected. So we cap the incremented value.
    update_data_generation_requests(canarydrop, count)
