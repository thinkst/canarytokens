import enum
import json
import math
import random
import string

from canarytokens.aws_infra.db_queries import get_current_assets
from canarytokens.aws_infra import data_generation
from canarytokens.aws_infra.state_management import is_ingesting
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetType
from canarytokens.settings import FrontendSettings
import asyncio

settings = FrontendSettings()


class AssetLabel(str, enum.Enum):
    """
    Enum for asset labels used in the AWS infrastructure.
    """

    BUCKET_NAME = "bucket_name"
    OBJECTS = "objects"
    OBJECT_PATH = "object_path"
    SQS_QUEUE_NAME = "sqs_queue_name"
    SSM_PARAMETER_NAME = "ssm_parameter_name"
    SECRET_NAME = "secret_name"
    TABLE_NAME = "table_name"
    TABLE_ITEMS = "table_items"
    TABLE_ITEM = "table_item"


_ASSET_TYPE_CONFIG = {
    AWSInfraAssetType.S3_BUCKET: {
        "max_assets": 10,
        "asset_key": AssetLabel.BUCKET_NAME,
        "child_asset_key": AssetLabel.OBJECTS,
        "max_child_items": 20,
    },
    AWSInfraAssetType.SQS_QUEUE: {
        "max_assets": 10,
        "asset_key": AssetLabel.SQS_QUEUE_NAME,
    },
    AWSInfraAssetType.SSM_PARAMETER: {
        "max_assets": 10,
        "asset_key": AssetLabel.SSM_PARAMETER_NAME,
    },
    AWSInfraAssetType.SECRETS_MANAGER_SECRET: {
        "max_assets": 10,
        "asset_key": AssetLabel.SECRET_NAME,
    },
    AWSInfraAssetType.DYNAMO_DB_TABLE: {
        "max_assets": 10,
        "asset_key": AssetLabel.TABLE_NAME,
        "child_asset_key": AssetLabel.TABLE_ITEMS,
        "max_child_items": 20,
    },
}


def generate_tf_variables(canarydrop: Canarydrop, plan: dict) -> dict:
    """
    Generate variables to be used in the terraform template.
    """
    tf_variables = {
        "s3_bucket_names": [],
        "s3_objects": [],
        "sqs_queues": [],
        "ssm_parameters": [],
        "secrets": [],
        "tables": [],
        "table_items": [],
        "canarytoken_id": canarydrop.canarytoken.value(),
        "target_bus_arn": _get_ingestion_bus_arn(
            canarydrop.aws_infra_ingestion_bus_name
        ),
        "account_id": canarydrop.aws_account_id,
        "region": canarydrop.aws_region,
    }
    for bucket in plan["S3Bucket"]:
        tf_variables["s3_bucket_names"].append(bucket[AssetLabel.BUCKET_NAME])
        for s3_object in bucket.get("objects", []):
            tf_variables["s3_objects"].append(
                {
                    "bucket": bucket[AssetLabel.BUCKET_NAME],
                    "key": s3_object,
                    "content": "".join(
                        random.choice(
                            string.ascii_letters + string.digits,
                            k=random.randint(5, 1000),
                        )
                    ),
                }
            )
    return tf_variables


async def _add_assets_for_type(
    asset_type: AWSInfraAssetType,
    aws_deployed_assets: dict,
    aws_inventoried_assets: dict,
    plan: dict,
):
    """
    Add assets of a specific type to the plan.
    """
    count = _get_decoy_asset_count(
        aws_inventoried_assets,
        asset_type,
        aws_deployed_assets,
    )
    if count <= 0:
        return

    asset_names = await data_generation.generate_names(
        asset_type, aws_inventoried_assets.get(asset_type, []), count
    )

    config = _ASSET_TYPE_CONFIG[asset_type]
    asset_name_key = config["asset_key"]

    assets = []
    for asset_name in asset_names:
        asset = {asset_name_key: asset_name, "off_inventory": False}
        # Add type-specific child assets if they exist
        if child_asset_name_key := config.get("child_asset_key"):
            asset[child_asset_name_key] = []
        assets.append(asset)
    plan[asset_type].extend(assets)


def _get_decoy_asset_count(
    aws_inventoried_assets,
    asset_type: AWSInfraAssetType,
    aws_deployed_assets,
) -> int:
    return min(
        max(
            math.ceil(math.log2(len(aws_inventoried_assets.get(asset_type, [])) + 1)),
            1,
        ),
        _ASSET_TYPE_CONFIG[asset_type]["max_assets"]
        - len(aws_deployed_assets.get(asset_type, [])),
    )


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
        asset_key = config["asset_key"]

        for asset_name in aws_deployed_assets.get(asset_type, []):
            asset = {
                asset_key: asset_name,
                "off_inventory": asset_name
                not in aws_inventoried_assets.get(asset_type, []),
            }

            # get the child assets (objects or table items) from the last saved plan
            if child_asset_key := config.get("child_asset_key"):
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

    if is_ingesting(canarydrop):
        return proposed_plan

    await add_new_assets_to_plan(
        aws_deployed_assets, aws_inventoried_assets, proposed_plan
    )
    add_current_assets_to_plan(
        aws_deployed_assets, aws_inventoried_assets, proposed_plan, current_plan
    )
    return proposed_plan


def _get_ingestion_bus_arn(bus_name: str):
    return f"arn:aws:events:eu-west-1:{settings.AWS_INFRA_AWS_ACCOUNT}:event-bus/{bus_name}"


async def _generate_parent_asset_name(
    asset_type: AWSInfraAssetType, inventory: list
) -> str:
    """Generate a parent asset name (S3 bucket, SQS queue, etc.)."""
    names = (
        await data_generation.generate_names(asset_type, inventory, 1)
    ).suggested_names
    return names[0]


async def _generate_child_asset_name(
    asset_type: AWSInfraAssetType, parent_name: str
) -> str:
    """Generate a child asset name (S3 object, DynamoDB item, etc.)."""
    if not parent_name:
        raise ValueError(
            f"Parent asset name required for {asset_type.value} child generation"
        )

    names = await data_generation.generate_children_names(asset_type, parent_name, 1)
    return names[0]


async def generate_data_choice(
    canarydrop: Canarydrop,
    asset_type: AWSInfraAssetType,
    asset_field: str,
    parent_asset_name: str = None,
) -> str:
    """Generate a random data choice for the given asset type and field."""
    inventory = get_current_assets(canarydrop).get(asset_type, [])

    # Parent asset types (top-level resources)
    PARENT_FIELDS = {
        AssetLabel.BUCKET_NAME,
        AssetLabel.SQS_QUEUE_NAME,
        AssetLabel.SSM_PARAMETER_NAME,
        AssetLabel.SECRET_NAME,
        AssetLabel.TABLE_NAME,
    }

    # Child asset types (nested resources)
    CHILD_FIELDS = {
        AssetLabel.OBJECT_PATH,
        AssetLabel.TABLE_ITEM,
    }

    if asset_field in PARENT_FIELDS:
        return await _generate_parent_asset_name(asset_type, inventory)
    elif asset_field in CHILD_FIELDS:
        return await _generate_child_asset_name(asset_type, parent_asset_name)
    else:
        raise ValueError(f"Unsupported asset field: {asset_field}")


async def generate_child_assets(
    assets: dict[str, list[str]]
) -> dict[str, dict[str, list[str]]]:
    """
    Generate child assets for the given assets.
    """
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
                    random.randint(
                        1, _ASSET_TYPE_CONFIG[asset_type]["max_child_items"]
                    ),
                )
            )
    all_names: list[list[str]] = await asyncio.gather(
        *tasks
    )  # each task returns a list of names

    i = 0
    for asset_type, asset_names in assets.items():
        for asset_name in asset_names:
            result[asset_type][asset_name] = all_names[i]
            i += 1

    return result


def save_plan(canarydrop: Canarydrop, plan: dict[str, list[dict]]) -> None:
    """
    Save an AWS Infra plan and upload it to the tf modules S3 bucket.
    """
    canarydrop.aws_saved_plan = json.dumps(plan)
    canarydrop.aws_deployed_assets = json.dumps(
        {
            AWSInfraAssetType.S3_BUCKET.value: [
                bucket[AssetLabel.BUCKET_NAME]
                for bucket in plan.get(AWSInfraAssetType.S3_BUCKET.value, [])
            ],
            AWSInfraAssetType.DYNAMO_DB_TABLE.value: [
                table[AssetLabel.TABLE_NAME]
                for table in plan.get(AWSInfraAssetType.DYNAMO_DB_TABLE.value, [])
            ],
            AWSInfraAssetType.SQS_QUEUE.value: [
                queue[AssetLabel.SQS_QUEUE_NAME]
                for queue in plan.get(AWSInfraAssetType.SQS_QUEUE.value, [])
            ],
            AWSInfraAssetType.SSM_PARAMETER.value: [
                param[AssetLabel.SSM_PARAMETER_NAME]
                for param in plan.get(AWSInfraAssetType.SSM_PARAMETER.value, [])
            ],
            AWSInfraAssetType.SECRETS_MANAGER_SECRET.value: [
                secret[AssetLabel.SECRET_NAME]
                for secret in plan.get(
                    AWSInfraAssetType.SECRETS_MANAGER_SECRET.value, []
                )
            ],
        }
    )
