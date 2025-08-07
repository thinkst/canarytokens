import asyncio
import json
import math
import random
import re

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field, root_validator, validator, ValidationError

from canarytokens.aws_infra.aws_management import s3_bucket_is_available
from canarytokens.aws_infra.db_queries import get_current_assets
from canarytokens.aws_infra import data_generation
from canarytokens.aws_infra.state_management import is_ingesting
from canarytokens.aws_infra.utils import (
    DYNAMO_DB_TABLE_NAME_REGEX,
    S3_BUCKET_NAME_REGEX,
    S3_OBJECT_REGEX,
    SECRETS_MANAGER_NAME_REGEX,
    SQS_QUEUE_NAME_REGEX,
    SSM_PARAMETER_NAME_REGEX,
    TABLE_ITEM_REGEX,
)
from canarytokens.canarydrop import Canarydrop
from canarytokens.exceptions import AWSInfraDataGenerationLimitReached
from canarytokens.models import AWSInfraAssetField, AWSInfraAssetType
from canarytokens.settings import FrontendSettings

settings = FrontendSettings()


class AWSInfraAsset(BaseModel):
    """Individual asset within an AWS infrastructure plan."""

    bucket_name: Optional[str] = None
    sqs_queue_name: Optional[str] = None
    ssm_parameter_name: Optional[str] = None
    secret_name: Optional[str] = None
    table_name: Optional[str] = None
    objects: Optional[list[str]] = Field(default_factory=list)
    table_items: Optional[list[str]] = Field(default_factory=list)
    off_inventory: bool = False

    @validator("bucket_name")
    def validate_bucket_name(cls, name: str):
        if name is not None:
            if not re.match(S3_BUCKET_NAME_REGEX, name):
                raise ValueError(
                    f"S3 bucket name must be 3-63 characters, lowercase letters, numbers, dots, and hyphens only, invalid name: {name}"
                )

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
                raise ValueError(
                    f"S3 bucket name uses reserved prefix or suffix, invalid name: {name}"
                )

        return name

    @validator("sqs_queue_name")
    def validate_sqs_queue_name(cls, name: str):
        if name is not None:
            if not re.match(SQS_QUEUE_NAME_REGEX, name):
                raise ValueError(
                    f"SQS queue name must be 1-80 characters, alphanumeric, underscore, hyphen, semicolon only, invalid name: {name}"
                )
        return name

    @validator("ssm_parameter_name")
    def validate_ssm_parameter_name(cls, name: str):
        if name is not None:
            if not (1 <= len(name) <= 2048):
                raise ValueError(
                    f"SSM parameter name must be 1-2048 characters, invalid name: {name}"
                )

            if name in ("aws", "ssm"):
                raise ValueError(
                    f'SSM parameter name cannot contain reserved words "aws" or "ssm", invalid name: {name}'
                )
            if not re.fullmatch(SSM_PARAMETER_NAME_REGEX, name):
                raise ValueError(
                    f"SSM parameter name segments must be alphanumeric, underscore, dot, hyphen only, invalid segment: {name}"
                )
        return name

    @validator("secret_name")
    def validate_secret_name(cls, name: str):
        if name is not None:
            if not re.match(SECRETS_MANAGER_NAME_REGEX, name):
                raise ValueError(
                    f"Secrets Manager name must be 1-512 characters, no consecutive dots, invalid name: {name}"
                )
        return name

    @validator("table_name")
    def validate_table_name(cls, name: str):
        if name is not None:
            if not re.match(DYNAMO_DB_TABLE_NAME_REGEX, name):
                raise ValueError(
                    f"DynamoDB table name must be 3-255 characters, alphanumeric, underscore, dot, hyphen only, invalid name: {name}"
                )
        return name

    @validator("objects")
    def validate_objects_list(cls, names: list[str]):
        if names is not None:
            if len(names) != len(set(names)):
                raise ValueError(
                    f"S3Bucket objects must be unique within a bucket, duplicates found: {', '.join(set(name for name in names if names.count(name) > 1))}"
                )
            for name in names:
                if not re.match(S3_OBJECT_REGEX, name):
                    raise ValueError(
                        f"S3 object must be 1-1024 characters, invalid name: {name}"
                    )
        return names

    @validator("table_items")
    def validate_table_items_list(cls, names: list[str]):
        if names is not None:
            if len(names) != len(set(names)):
                raise ValueError(
                    f"DynamoDB table items must be unique within a table, duplicates found: {', '.join(set(name for name in names if names.count(name) > 1))}"
                )
            for name in names:
                if not re.match(TABLE_ITEM_REGEX, name):
                    raise ValueError(
                        f"DynamoDB table item must be 1-1024 characters, invalid name: {name}"
                    )
        return names


class AWSInfraPlan(BaseModel):
    """AWS Infrastructure plan containing assets by type."""

    S3Bucket: list[AWSInfraAsset] = Field(default_factory=list, alias="S3Bucket")
    SQSQueue: list[AWSInfraAsset] = Field(default_factory=list, alias="SQSQueue")
    SSMParameter: list[AWSInfraAsset] = Field(
        default_factory=list, alias="SSMParameter"
    )
    SecretsManagerSecret: list[AWSInfraAsset] = Field(
        default_factory=list, alias="SecretsManagerSecret"
    )
    DynamoDBTable: list[AWSInfraAsset] = Field(
        default_factory=list, alias="DynamoDBTable"
    )

    # Store validation errors as a list
    validation_errors: Optional[list[str]] = None

    @root_validator
    def validate_unique_names(cls, values):
        """Ensure no duplicate asset names within each type."""
        validation_errors = []

        canarydrop = values.get("_canarydrop")
        if canarydrop is None:
            account_inventory = {}
        else:
            account_inventory = get_current_assets(canarydrop)

        for asset_type in AWSInfraAssetType:
            field_name = _ASSET_TYPE_CONFIG[asset_type].asset_field_name.value
            new_names = [
                getattr(asset, field_name)
                for asset in values.get(asset_type.value, [])
                if getattr(asset, field_name, None)
            ]
            if len(new_names) != len(set(new_names)):
                validation_errors.append(
                    f"Duplicate {asset_type} names found in plan: {', '.join(set(name for name in new_names if new_names.count(name) > 1))}"
                )

            if account_assets := account_inventory.get(asset_type):
                inventory_plan_intersection = set(new_names) & set(account_assets)
                if len(inventory_plan_intersection) > 0:
                    validation_errors.append(
                        f"{asset_type} names ({', '.join(inventory_plan_intersection)}) already exists in AWS account"
                    )

        if validation_errors:
            values["validation_errors"] = list(
                set(validation_errors)
            )  # Remove duplicates
        return values

    @root_validator
    def validate_max_number_assets(cls, values):
        """Ensure the number of assets does not exceed the maximum allowed."""
        validation_errors = []
        for asset_type, config in _ASSET_TYPE_CONFIG.items():
            current_count = len(values.get(asset_type.value, []))
            if current_count > config.max_assets:
                validation_errors.append(
                    f"Exceeded maximum number of {asset_type} decoy assets: {current_count} > {config.max_assets}"
                )
        if validation_errors:
            values["validation_errors"] = validation_errors
        return values

    @classmethod
    def from_dict_with_canarydrop(
        cls, plan_dict: dict, canarydrop: Canarydrop
    ) -> "AWSInfraPlan":
        """
        Create an AWSInfraPlan from a dictionary with canarydrop context for validation.
        """
        try:
            # Attach canarydrop context to the plan_dict for validation
            plan_extended = plan_dict.copy()
            plan_extended["_canarydrop"] = canarydrop
            return cls.parse_obj(plan_extended)
        except ValidationError as e:
            plan = cls()
            plan.validation_errors = [f"{error['msg']}" for error in e.errors()]
            return plan

    class Config:
        allow_population_by_field_name = True


@dataclass
class AssetTypeConfig:
    max_assets: int
    asset_field_name: AWSInfraAssetField
    child_asset_field_name: Optional[AWSInfraAssetField] = None
    max_child_items: Optional[int] = None


_ASSET_TYPE_CONFIG = {
    AWSInfraAssetType.S3_BUCKET: AssetTypeConfig(
        10, AWSInfraAssetField.BUCKET_NAME, AWSInfraAssetField.OBJECTS, 20
    ),
    AWSInfraAssetType.SQS_QUEUE: AssetTypeConfig(5, AWSInfraAssetField.SQS_QUEUE_NAME),
    AWSInfraAssetType.SSM_PARAMETER: AssetTypeConfig(
        10, AWSInfraAssetField.SSM_PARAMETER_NAME
    ),
    AWSInfraAssetType.SECRETS_MANAGER_SECRET: AssetTypeConfig(
        5, AWSInfraAssetField.SECRET_NAME
    ),
    AWSInfraAssetType.DYNAMO_DB_TABLE: AssetTypeConfig(
        10, AWSInfraAssetField.TABLE_NAME, AWSInfraAssetField.TABLE_ITEMS, 20
    ),
}


async def _add_assets_for_type(
    asset_type: AWSInfraAssetType,
    aws_deployed_assets: dict,
    aws_inventoried_assets: dict,
    plan: dict,
):
    """
    Add assets of a specific type to the plan.
    """
    inventory_count = len(aws_inventoried_assets.get(asset_type) or [])
    scaled_decoy_count = math.ceil(math.log2(inventory_count + 1)) or 1
    deployed_decoy_count_remaining = _ASSET_TYPE_CONFIG[asset_type].max_assets - len(
        aws_deployed_assets.get(asset_type, [])
    )
    decoy_asset_count = min(deployed_decoy_count_remaining, scaled_decoy_count)

    if decoy_asset_count <= 0:
        return

    asset_names = (
        await data_generation.generate_names(
            asset_type, aws_inventoried_assets.get(asset_type, []), decoy_asset_count
        )
    ).suggested_names

    config = _ASSET_TYPE_CONFIG[asset_type]

    assets = []
    for asset_name in asset_names:
        asset = {config.asset_field_name: asset_name, "off_inventory": False}
        # Add type-specific child assets if they exist
        if child_asset_name_key := config.child_asset_field_name:
            asset[child_asset_name_key] = []
        assets.append(asset)
    plan[asset_type].extend(assets)


async def add_new_assets_to_plan(
    aws_deployed_assets: dict, aws_inventoried_assets: dict, plan: dict
):
    """
    Asynchronously add new decoy AWS assets to the plan based on the current deployed and inventoried assets.
    """
    # Create tasks for all asset types
    tasks = []
    for asset_type in _ASSET_TYPE_CONFIG:
        tasks.append(
            _add_assets_for_type(
                asset_type, aws_deployed_assets, aws_inventoried_assets, plan
            )
        )

    await asyncio.gather(*tasks)


def add_current_assets_to_plan(
    aws_deployed_assets: dict,
    aws_inventoried_assets: dict,
    proposed_plan: dict,
    current_plan: dict,
):
    """
    Add current deployed assets to the proposed plan.
    """
    for asset_type, config in _ASSET_TYPE_CONFIG.items():
        asset_key = config.asset_field_name

        for asset_name in aws_deployed_assets.get(asset_type, []):
            asset = {
                asset_key: asset_name,
                "off_inventory": asset_name
                not in aws_inventoried_assets.get(asset_type, []),
            }

            # get the child assets (objects or table items) from the last saved plan
            if child_asset_key := config.child_asset_field_name:
                for last_saved_parent_asset in current_plan.get(asset_type, [{}]):
                    if last_saved_parent_asset.get(asset_key) == asset_name:
                        asset[child_asset_key] = last_saved_parent_asset.get(
                            child_asset_key, []
                        )
                        break

            proposed_plan[asset_type].append(asset)


async def generate_proposed_plan(canarydrop: Canarydrop) -> dict:
    """
    Return a proposed plan for decoy assets containing new and current assets.
    """

    aws_deployed_assets = json.loads(canarydrop.aws_deployed_assets or "{}")
    aws_inventoried_assets = get_current_assets(canarydrop)
    current_plan = json.loads(canarydrop.aws_saved_plan or "{}")
    proposed_plan = {asset_type.value: [] for asset_type in AWSInfraAssetType}

    # If the plan of an existing canarytoken is being edited, return the previous plan,
    # but check if assets part of previous plan have been deleted.
    if is_ingesting(canarydrop):
        add_current_assets_to_plan(
            aws_deployed_assets, aws_inventoried_assets, proposed_plan, current_plan
        )
        return proposed_plan

    # If multiple inventories have been performed, but the user has not saved the plan,
    # We should not use Gemini anymore, and stop the user from increasing our costs.
    if not data_generation.name_generation_limit_usage(canarydrop).remaining:
        raise AWSInfraDataGenerationLimitReached(
            f"Name generation limit reached for canarytoken {canarydrop.canarytoken.value()}."
        )

    await add_new_assets_to_plan(
        aws_deployed_assets, aws_inventoried_assets, proposed_plan
    )
    data_generation.name_generation_usage_consume(canarydrop, len(proposed_plan.keys()))
    return proposed_plan


def _extract_current_names(
    current_plan: dict,
    asset_type: AWSInfraAssetType,
    parent_asset_name: str = None,
    is_child_asset: bool = False,
) -> list[str]:
    """
    Extract current names from the plan for the given asset type and field.
    """
    if not is_child_asset:
        return [
            asset[_ASSET_TYPE_CONFIG[asset_type].asset_field_name]
            for asset in current_plan.get(asset_type, [])
        ]
    else:
        for asset in current_plan.get(asset_type, []):
            if (
                asset.get(_ASSET_TYPE_CONFIG[asset_type].asset_field_name)
                == parent_asset_name
            ):
                return asset.get(
                    _ASSET_TYPE_CONFIG[asset_type].child_asset_field_name, []
                )
    return []


async def generate_data_choice(
    canarydrop: Canarydrop,
    asset_type: AWSInfraAssetType,
    asset_field: AWSInfraAssetField,
    parent_asset_name: AWSInfraAssetField = None,
    current_plan: dict = None,
) -> str:
    """Generate a random data choice for the given asset type and field."""

    if not data_generation.name_generation_limit_usage(canarydrop).remaining:
        raise AWSInfraDataGenerationLimitReached(
            f"Name generation limit reached for canarytoken {canarydrop.canarytoken.value()}."
        )

    VALID_FIELDS = {
        AWSInfraAssetType.S3_BUCKET: [
            AWSInfraAssetField.BUCKET_NAME,
            AWSInfraAssetField.OBJECTS,
        ],
        AWSInfraAssetType.SQS_QUEUE: [AWSInfraAssetField.SQS_QUEUE_NAME],
        AWSInfraAssetType.SSM_PARAMETER: [AWSInfraAssetField.SSM_PARAMETER_NAME],
        AWSInfraAssetType.SECRETS_MANAGER_SECRET: [AWSInfraAssetField.SECRET_NAME],
        AWSInfraAssetType.DYNAMO_DB_TABLE: [
            AWSInfraAssetField.TABLE_NAME,
            AWSInfraAssetField.TABLE_ITEMS,
        ],
    }
    if asset_field not in VALID_FIELDS[asset_type]:
        raise ValueError(
            f"Invalid asset type and field combination: {asset_type}, {asset_field}"
        )

    inventory = get_current_assets(canarydrop).get(asset_type, [])

    # Child asset types (nested resources)
    CHILD_FIELDS = {
        AWSInfraAssetField.OBJECTS,
        AWSInfraAssetField.TABLE_ITEMS,
    }

    is_child_asset = asset_field in CHILD_FIELDS

    if is_child_asset and not parent_asset_name:
        raise ValueError(
            f"Parent asset name required for {asset_type.value} child generation"
        )
    current_plan = current_plan or {}

    current_names = _extract_current_names(
        current_plan,
        asset_type,
        parent_asset_name,
        is_child_asset=is_child_asset,
    )

    max_attempts = 3
    for _ in range(max_attempts):
        if not is_child_asset:
            names = (
                await data_generation.generate_names(
                    asset_type, inventory, trim_list=False
                )
            ).suggested_names
        else:
            names = await data_generation.generate_children_names(
                asset_type, parent_asset_name, trim_list=False
            )
        result = next((name for name in names if name not in current_names), None)
        if result:
            break
    if result is None:
        raise ValueError(
            f"Could not generate a unique name for {asset_type.value} with field {asset_field.value} after {max_attempts} attempts."
        )
    data_generation.name_generation_usage_consume(canarydrop)
    return result


async def generate_child_assets(
    canarydrop: Canarydrop, assets: dict[str, list[str]]
) -> dict[str, dict[str, list[str]]]:
    """
    Generate child assets for the given assets.
    """
    if not data_generation.name_generation_limit_usage(canarydrop).remaining:
        raise AWSInfraDataGenerationLimitReached(
            f"Name generation limit reached for canarytoken {canarydrop.canarytoken.value()}."
        )

    result = {
        AWSInfraAssetType.S3_BUCKET.value: {},
        AWSInfraAssetType.DYNAMO_DB_TABLE.value: {},
    }
    tasks = []
    for asset_type, asset_names in assets.items():
        for asset_name in asset_names:
            tasks.append(
                data_generation.generate_children_names(
                    asset_type,
                    asset_name,
                    random.randint(1, _ASSET_TYPE_CONFIG[asset_type].max_child_items),
                )
            )
    all_names: list[list[str]] = await asyncio.gather(
        *tasks
    )  # each task returns a list of names
    data_generation.name_generation_usage_consume(canarydrop, len(all_names))

    i = 0
    for asset_type, asset_names in assets.items():
        for asset_name in asset_names:
            result[asset_type][asset_name] = all_names[i]
            i += 1

    return result


async def save_plan(canarydrop: Canarydrop, plan: dict[str, list[dict]]) -> None:
    """
    Save an AWS Infra plan with validation using canarydrop context.
    """
    current_deployed_assets = json.loads(canarydrop.aws_deployed_assets or "{}")
    try:
        canarydrop.aws_deployed_assets = json.dumps(
            {
                AWSInfraAssetType.S3_BUCKET.value: [
                    bucket[AWSInfraAssetField.BUCKET_NAME]
                    for bucket in plan.get(AWSInfraAssetType.S3_BUCKET.value, [])
                ],
                AWSInfraAssetType.DYNAMO_DB_TABLE.value: [
                    table[AWSInfraAssetField.TABLE_NAME]
                    for table in plan.get(AWSInfraAssetType.DYNAMO_DB_TABLE.value, [])
                ],
                AWSInfraAssetType.SQS_QUEUE.value: [
                    queue[AWSInfraAssetField.SQS_QUEUE_NAME]
                    for queue in plan.get(AWSInfraAssetType.SQS_QUEUE.value, [])
                ],
                AWSInfraAssetType.SSM_PARAMETER.value: [
                    param[AWSInfraAssetField.SSM_PARAMETER_NAME]
                    for param in plan.get(AWSInfraAssetType.SSM_PARAMETER.value, [])
                ],
                AWSInfraAssetType.SECRETS_MANAGER_SECRET.value: [
                    secret[AWSInfraAssetField.SECRET_NAME]
                    for secret in plan.get(
                        AWSInfraAssetType.SECRETS_MANAGER_SECRET.value, []
                    )
                ],
            }
        )
    except KeyError:
        raise ValueError(
            "Invalid plan structure. Ensure all required fields are present in the plan."
        )
    plan_object = AWSInfraPlan.from_dict_with_canarydrop(plan, canarydrop)
    if plan_object.validation_errors:
        canarydrop.aws_deployed_assets = json.dumps(current_deployed_assets)
        raise ValueError(f"{'; '.join(plan_object.validation_errors)}")

    tasks = []
    new_buckets = [
        bucket
        for bucket in plan_object.S3Bucket
        if bucket.bucket_name
        not in current_deployed_assets.get(AWSInfraAssetType.S3_BUCKET, [])
    ]
    for bucket in new_buckets:
        tasks.append(s3_bucket_is_available(bucket.bucket_name))

    results = await asyncio.gather(*tasks)
    unavailable_buckets = []
    for bucket, is_available in zip(new_buckets, results):
        if not is_available:
            unavailable_buckets.append(bucket.bucket_name)

    if unavailable_buckets:
        canarydrop.aws_deployed_assets = json.dumps(current_deployed_assets)
        raise ValueError(f"S3 buckets not available: {', '.join(unavailable_buckets)}")

    # Remove canarydrop from plan before serializing
    plan_to_save = {k: v for k, v in plan.items() if k != "_canarydrop"}
    canarydrop.aws_saved_plan = json.dumps(plan_to_save)
