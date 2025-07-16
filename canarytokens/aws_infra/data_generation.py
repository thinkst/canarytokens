from dataclasses import dataclass, field
from difflib import SequenceMatcher

# from google import genai
import logging
from typing import List

import re
import requests
import json
import random
import httpx

from canarytokens.models import AWSInfraAssetType
from canarytokens.settings import FrontendSettings

settings = FrontendSettings()


def _get_system_prompt():
    return """
You are a deception expert tasked with generating **decoy AWS resource names** for early-warning AWS resource tripwires that will alert the customer when an attacker interacts with them.
You have analyzed recent AWS breaches and attacks and have access to all threat intelligence data available. You are aware of the common patterns and naming conventions used in AWS environments.

Scope:
• Amazon S3 buckets
• Amazon DynamoDB tables
• AWS Systems Manager (SSM) Parameter Store parameters
• Amazon SQS queues (standard only)
• AWS Secrets Manager secrets

Strictly enforce these rules when generating names:
1. Very important - Preserve each inventory's **style cues** (prefixes, kebab/camel/snake-case, environment tags like "-prod"), but randomise actual nouns/IDs.
2. If names in the provided inventory have suffixes that seem random, do not suggest names with any random suffixes, we will add our own random suffixes to the names later.
3. The names should look like they could be found in the same environment and they blend in with the existing resources. They should not look like they are from a different environment or region.
4. The names should be **believable** and **attractive to attackers**. They should look like real AWS resources that might be found in a production environment. They should not look like obviously fake or suspicious resources.
5. The name should attract attackers to interact with the resource.
6. Do not use the word "decoy" or "canary" in the name, as it will instantly reveal the resource as a trap.
7. Make up names for services that might seem like likely targets for attackers especially during reconnaissance phase - be creative, the names should instantly get the attention of an attacker.
8. Never add a region identifier to the name, e.g. "-eu-west-1" or "-us-east-2", as it is not a common practice in AWS resource names.
9. If the inventory doesn't seem to have a satisfactory pattern, make up project code names or use placeholder names that could make the resource look obscure or mysterious.
10. if there are varying case styles or naming conventions used for names in the inventory, ensure that the generated names follow the same conventions. Produce a mix of kebab-case, snake_case, camelCase, and PascalCase as appropriate.
"""


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
            "temperature": 0.8,
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
        # self._client = genai.Client(api_key=GEMINI_API_KEY)
        self._GEMINI_MODEL = "gemini-2.5-flash"
        self._GEMINI_API_KEY = settings.GEMINI_API_KEY
        self._prompt_template = "In line with your system instructions, generate a list of {count} decoy asset names for the following AWS service that would fit into the provided inventory. The generated decoy asset names should look similar to the assets in the inventory. If the list for the service type in the provided inventory is empty, still return a list of {count} names.\n{service} inventory: {inventory}"
        self._GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{self._GEMINI_MODEL}:generateContent"

    def generate_names(
        self, asset_type: AWSInfraAssetType, inventory: list[str], count=5
    ) -> Suggestion:
        """
        Generate decoy names for the specified AWS asset type based on the provided inventory.
        :param asset_type: The type of AWS asset to generate names for.
        :param inventory: A list of existing names for the specified asset type.
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
            new_names = self._get_suggested_names(
                asset_type, inventory, count=overshoot
            )
            logging.info("Names generated by Gemini: %s", new_names)
            validated_names.extend(
                self._trim_list(asset_type, inventory, new_names, count)
            )

        random.shuffle(validated_names)
        suggested_names = validated_names[:count]

        return Suggestion(asset_type, suggested_names)

    def _validate_s3_name(self, name: str) -> bool:
        # 3-63 chars, lowercase a-z 0-9 . - ; begin/end alphanumeric; no IP-style; no reserved prefixes/suffixes
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

        # Try to access the bucket unauthenticated; if 200 or 403, it exists
        url = f"https://{name}.s3.amazonaws.com"
        try:
            resp = requests.head(url, timeout=2)
            bucket_exists = resp.status_code in (200, 403) and resp.status_code != 404
        except requests.RequestException:
            return False

        if not bucket_exists:
            return True

        # print(f"S3 bucket '{name}' already exists.")
        return False
        # return True

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

    def _validate_name(self, asset_type: AWSInfraAssetType, name: str) -> bool:
        """
        Validate a name against the rules for the specified AWS asset type.
        :param asset_type: The type of AWS asset to validate the name for.
        :param name: The name to validate.
        :return: True if the name is valid, False otherwise.
        """
        validator = self._validator_map.get(asset_type)
        if not validator:
            raise ValueError(f"No validator found for asset type {asset_type.name}.")

        return validator(name)

    def _similarity_score(self, name, inventory):
        return max(
            (SequenceMatcher(None, name, existing).ratio() for existing in inventory),
            default=0,
        )

    def _trim_list(
        self,
        asset_type: AWSInfraAssetType,
        inventory: list[str],
        suggested_names: list[str],
        count: int,
    ) -> list[str]:
        """
        Get a list of validated names from the provided inventory.
        :param asset_type: The type of AWS asset to validate names for.
        :param inventory: A list of existing names for the specified asset type.
        :param count: The number of names to return.
        :return: A list of validated names.
        """
        assert count > 0, "Count must be a positive integer."

        return list(
            filter(
                lambda name: self._validate_name(asset_type, name)
                and not self._similarity_score(name, inventory) >= 0.9,
                suggested_names,
            )
        )

    def _get_post_data(self, prompt: str):
        return {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                # "temperature": self._gemini_config["temperature"],
                "responseMimeType": self._gemini_config["response_mime_type"],
                "responseSchema": self._gemini_config["response_schema"],
            },
            "systemInstruction": {
                "parts": [{"text": self._gemini_config["system_instruction"]}]
            },
        }

    def _get_suggested_names(
        self, asset_type: AWSInfraAssetType, inventory: list[str], count=5
    ):
        """
        Get suggested names from Gemini for the specified asset type based on the provided inventory.
        :param asset_type: The type of AWS asset to generate names for.
        :param inventory: A list of existing names for the specified asset type.
        :param count: The number of names to generate.
        :return: A list of suggested names.
        """
        assert count > 0, "Count must be a positive integer."

        logging.info(inventory)

        prompt = self._prompt_template.format(
            count=count, service=asset_type.value, inventory=",".join(inventory)
        )

        logging.info("Prompt sent to Gemini: %s", prompt)

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self._GEMINI_API_KEY,
        }

        try:
            response = httpx.post(
                self._GEMINI_API_URL,
                headers=headers,
                json=self._get_post_data(prompt),
                timeout=60,
            )
            response.raise_for_status()

            result = response.json()
            parsed_content = json.loads(
                result["candidates"][0]["content"]["parts"][0]["text"]
            )

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get response from Gemini API: {e}")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to parse response from Gemini API: {e}")

        return parsed_content.get("suggested_names", [])
