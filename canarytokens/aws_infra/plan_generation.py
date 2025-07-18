import enum
import json
import math
import random
import string

from canarytokens.aws_infra.db_queries import get_current_assets
from canarytokens.aws_infra.data_generation import GeminiDecoyNameGenerator
from canarytokens.aws_infra.state_management import is_ingesting
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetType
from canarytokens.settings import FrontendSettings
import asyncio

settings = FrontendSettings()

NAME_ENVS = ["prod", "staging", "dev", "testing"]
NAME_TARGETS = ["customer", "user", "admin", "audit"]
MAX_CHILD_ITEMS = 20
MAX_S3_BUCKETS = 10
MAX_DYNAMO_TABLES = 10
MAX_SSM_PARAMETERS = 10
MAX_SQS_QUEUES = 10
MAX_SECRET_MANAGER_SECRETS = 10


NAME_GENERATOR = GeminiDecoyNameGenerator()


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
    for bucket in plan["assets"]["S3Bucket"]:
        tf_variables["s3_bucket_names"].append(bucket[AssetLabel.BUCKET_NAME])
        for s3_object in bucket.get("objects", []):
            tf_variables["s3_objects"].append(
                {
                    "bucket": bucket[AssetLabel.BUCKET_NAME],
                    "key": s3_object,
                    "content": "".join(
                        [
                            random.choice(string.ascii_letters + string.digits)
                            for _ in range(random.randint(5, 1000))
                        ]
                    ),
                }
            )
    return tf_variables


async def generate_for_asset_type(
    asset_type: AWSInfraAssetType, inventory: list, count: int = 1
):
    suggested = await NAME_GENERATOR.generate_names(asset_type, inventory, count)
    return suggested.suggested_names


async def generate_objects_for_bucket(bucket, name_generator):
    count = random.randint(1, MAX_CHILD_ITEMS)
    bucket_name = bucket[AssetLabel.BUCKET_NAME]
    objects = await name_generator.generate_children_names(
        AWSInfraAssetType.S3_BUCKET,
        bucket_name,
        count,
    )
    bucket[AssetLabel.OBJECTS].extend(objects)


async def _add_s3_buckets(aws_deployed_assets, aws_inventoried_assets, plan):
    count = _get_decoy_asset_count(
        aws_inventoried_assets,
        AWSInfraAssetType.S3_BUCKET,
        aws_deployed_assets,
        MAX_S3_BUCKETS,
    )
    if count <= 0:
        return
    bucket_names = await generate_for_asset_type(
        AWSInfraAssetType.S3_BUCKET,
        aws_inventoried_assets.get(AWSInfraAssetType.S3_BUCKET.value, []),
        count,
    )
    plan["assets"][AWSInfraAssetType.S3_BUCKET.value].extend(
        [
            {AssetLabel.BUCKET_NAME: bucket_name, "objects": [], "off_inventory": False}
            for bucket_name in bucket_names
        ]
    )

    # Generate S3 objects for each bucket asynchronously
    await asyncio.gather(
        *[
            generate_objects_for_bucket(bucket, NAME_GENERATOR)
            for bucket in plan["assets"][AWSInfraAssetType.S3_BUCKET.value]
        ]
    )


async def _add_sqs_queues(aws_deployed_assets, aws_inventoried_assets, plan):
    count = _get_decoy_asset_count(
        aws_inventoried_assets,
        AWSInfraAssetType.SQS_QUEUE,
        aws_deployed_assets,
        MAX_SQS_QUEUES,
    )
    if count <= 0:
        return
    sqs_queue_names = await generate_for_asset_type(
        AWSInfraAssetType.SQS_QUEUE,
        aws_inventoried_assets.get(AWSInfraAssetType.SQS_QUEUE.value, []),
        count,
    )
    plan["assets"][AWSInfraAssetType.SQS_QUEUE.value].extend(
        [
            {AssetLabel.SQS_QUEUE_NAME: sqs_queue_name, "off_inventory": False}
            for sqs_queue_name in sqs_queue_names
        ]
    )


async def _add_ssm_parameters(aws_deployed_assets, aws_inventoried_assets, plan):
    count = _get_decoy_asset_count(
        aws_inventoried_assets,
        AWSInfraAssetType.SSM_PARAMETER,
        aws_deployed_assets,
        MAX_SSM_PARAMETERS,
    )
    if count <= 0:
        return
    ssm_parameter_names = await generate_for_asset_type(
        AWSInfraAssetType.SSM_PARAMETER,
        aws_inventoried_assets.get(AWSInfraAssetType.SSM_PARAMETER.value, []),
        count,
    )
    plan["assets"][AWSInfraAssetType.SSM_PARAMETER.value].extend(
        [
            {AssetLabel.SSM_PARAMETER_NAME: ssm_parameter_name, "off_inventory": False}
            for ssm_parameter_name in ssm_parameter_names
        ]
    )


async def _add_secret_manager_secrets(
    aws_deployed_assets, aws_inventoried_assets, plan
):
    count = _get_decoy_asset_count(
        aws_inventoried_assets,
        AWSInfraAssetType.SECRETS_MANAGER_SECRET,
        aws_deployed_assets,
        MAX_SECRET_MANAGER_SECRETS,
    )
    if count <= 0:
        return
    secret_names = await generate_for_asset_type(
        AWSInfraAssetType.SECRETS_MANAGER_SECRET,
        aws_inventoried_assets.get(AWSInfraAssetType.SECRETS_MANAGER_SECRET.value, []),
        count,
    )
    plan["assets"][AWSInfraAssetType.SECRETS_MANAGER_SECRET.value].extend(
        [
            {AssetLabel.SECRET_NAME: secret_name, "off_inventory": False}
            for secret_name in secret_names
        ]
    )


async def _add_dynamo_tables(aws_deployed_assets, aws_inventoried_assets, plan):
    count = _get_decoy_asset_count(
        aws_inventoried_assets,
        AWSInfraAssetType.DYNAMO_DB_TABLE,
        aws_deployed_assets,
        MAX_DYNAMO_TABLES,
    )
    if count <= 0:
        return
    table_names = await generate_for_asset_type(
        AWSInfraAssetType.DYNAMO_DB_TABLE,
        aws_inventoried_assets.get(AWSInfraAssetType.DYNAMO_DB_TABLE.value, []),
        count,
    )
    plan["assets"][AWSInfraAssetType.DYNAMO_DB_TABLE.value].extend(
        [
            {
                AssetLabel.TABLE_NAME: table_name,
                "off_inventory": False,
                "table_items": [],
            }
            for table_name in table_names
        ]
    )

    # Generate DynamoDB table items for each table asynchronously

    async def generate_items_for_table(table):
        count = random.randint(1, MAX_CHILD_ITEMS)
        table_name = table[AssetLabel.TABLE_NAME]
        items = await NAME_GENERATOR.generate_children_names(
            AWSInfraAssetType.DYNAMO_DB_TABLE,
            table_name,
            count,
        )
        table["table_items"].extend(items)

    await asyncio.gather(
        *[
            generate_items_for_table(table)
            for table in plan["assets"][AWSInfraAssetType.DYNAMO_DB_TABLE.value]
        ]
    )


def _get_decoy_asset_count(
    aws_inventoried_assets,
    asset_type: AWSInfraAssetType,
    aws_deployed_assets,
    MAX_ASSETS: int,
):
    return min(
        max(
            math.ceil(
                math.log2(len(aws_inventoried_assets.get(asset_type.value, [])) + 1)
            ),
            1,
        ),
        MAX_ASSETS - len(aws_deployed_assets.get(asset_type.value, [])),
    )


async def add_new_assets_to_plan(
    aws_deployed_assets: dict, aws_inventoried_assets: dict, plan: dict
):
    """
    Asynchronously add new decoy AWS assets to the plan based on the current deployed and inventoried assets.
    """
    await asyncio.gather(
        _add_s3_buckets(aws_deployed_assets, aws_inventoried_assets, plan),
        _add_sqs_queues(aws_deployed_assets, aws_inventoried_assets, plan),
        _add_ssm_parameters(aws_deployed_assets, aws_inventoried_assets, plan),
        _add_secret_manager_secrets(aws_deployed_assets, aws_inventoried_assets, plan),
        _add_dynamo_tables(aws_deployed_assets, aws_inventoried_assets, plan),
    )


def add_current_assets_to_plan(
    aws_deployed_assets: dict,
    aws_inventoried_assets: dict,
    proposed_plan: dict,
    current_plan: dict,
):
    # add current assets
    for bucket_name in aws_deployed_assets.get(AWSInfraAssetType.S3_BUCKET.value, []):
        objects = list(
            filter(
                lambda bucket: bucket[AssetLabel.BUCKET_NAME] == bucket_name,
                current_plan.get("assets", {}).get(
                    AWSInfraAssetType.S3_BUCKET.value, []
                ),
            )
        )[0].get("objects", [])
        proposed_plan["assets"][AWSInfraAssetType.S3_BUCKET.value].append(
            {
                AssetLabel.BUCKET_NAME: bucket_name,
                "objects": objects,
                "off_inventory": bucket_name
                not in aws_inventoried_assets.get(
                    AWSInfraAssetType.S3_BUCKET.value, []
                ),
            }
        )

    for sqs_queue_name in aws_deployed_assets.get(
        AWSInfraAssetType.SQS_QUEUE.value, []
    ):
        proposed_plan["assets"][AWSInfraAssetType.SQS_QUEUE.value].append(
            {
                AssetLabel.SQS_QUEUE_NAME: sqs_queue_name,
                "off_inventory": sqs_queue_name
                not in aws_inventoried_assets.get(
                    AWSInfraAssetType.SQS_QUEUE.value, []
                ),
            }
        )

    for ssm_parameter_name in aws_deployed_assets.get(
        AWSInfraAssetType.SSM_PARAMETER.value, []
    ):
        proposed_plan["assets"][AWSInfraAssetType.SSM_PARAMETER.value].append(
            {
                AssetLabel.SSM_PARAMETER_NAME: ssm_parameter_name,
                "off_inventory": ssm_parameter_name
                not in aws_inventoried_assets.get(
                    AWSInfraAssetType.SSM_PARAMETER.value, []
                ),
            }
        )

    for secret_name in aws_deployed_assets.get(
        AWSInfraAssetType.SECRETS_MANAGER_SECRET.value, []
    ):
        proposed_plan["assets"][AWSInfraAssetType.SECRETS_MANAGER_SECRET.value].append(
            {
                AssetLabel.SECRET_NAME: secret_name,
                "off_inventory": secret_name
                not in aws_inventoried_assets.get(
                    AWSInfraAssetType.SECRETS_MANAGER_SECRET.value, []
                ),
            }
        )

    for table_name in aws_deployed_assets.get(
        AWSInfraAssetType.DYNAMO_DB_TABLE.value, []
    ):
        table_items = list(
            filter(
                lambda table: table[AssetLabel.TABLE_NAME] == table_name,
                current_plan.get("assets", {}).get(
                    AWSInfraAssetType.DYNAMO_DB_TABLE.value, []
                ),
            )
        )[0].get("table_items", [])
        proposed_plan["assets"][AWSInfraAssetType.DYNAMO_DB_TABLE.value].append(
            {
                AssetLabel.TABLE_NAME: table_name,
                "off_inventory": table_name
                not in aws_inventoried_assets.get(
                    AWSInfraAssetType.DYNAMO_DB_TABLE.value, []
                ),
                "table_items": table_items,
            }
        )


async def generate_proposed_plan(canarydrop: Canarydrop):
    """
    Return a proposed plan for decoy assets containing new and current assets.
    """

    aws_deployed_assets = json.loads(canarydrop.aws_deployed_assets or "{}")
    aws_inventoried_assets = get_current_assets(canarydrop)
    current_plan = json.loads(canarydrop.aws_saved_plan or "{}")
    proposed_plan = {
        "assets": {asset_type.value: [] for asset_type in AWSInfraAssetType}
    }

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


def _get_inventory_for_asset_type(
    canarydrop: Canarydrop, asset_type: AWSInfraAssetType
) -> list:
    """Extract inventory for a specific asset type from canarydrop."""
    if not canarydrop or not canarydrop.aws_inventoried_assets:
        return []

    if isinstance(canarydrop.aws_inventoried_assets, dict):
        inventory = canarydrop.aws_inventoried_assets
    else:
        inventory = json.loads(canarydrop.aws_inventoried_assets)

    return inventory.get(asset_type.value, [])


async def _generate_parent_asset_name(
    asset_type: AWSInfraAssetType, inventory: list
) -> str:
    """Generate a parent asset name (S3 bucket, SQS queue, etc.)."""
    names = await generate_for_asset_type(asset_type, inventory, 1)
    return names[0]


async def _generate_child_asset_name(
    asset_type: AWSInfraAssetType, parent_name: str
) -> str:
    """Generate a child asset name (S3 object, DynamoDB item, etc.)."""
    if not parent_name:
        raise ValueError(
            f"Parent asset name required for {asset_type.value} child generation"
        )

    names = await NAME_GENERATOR.generate_children_names(asset_type, parent_name, 1)
    return names[0]


async def _generate_asset_by_type_and_field(
    asset_type: AWSInfraAssetType,
    asset_field: str,
    inventory: list,
    parent_asset_name: str = None,
) -> str:
    """Generate asset name based on type and field."""
    # Parent asset types (top-level resources)
    parent_fields = {
        AssetLabel.BUCKET_NAME,
        AssetLabel.SQS_QUEUE_NAME,
        AssetLabel.SSM_PARAMETER_NAME,
        AssetLabel.SECRET_NAME,
        AssetLabel.TABLE_NAME,
    }

    # Child asset types (nested resources)
    child_fields = {
        AssetLabel.OBJECT_PATH,
        AssetLabel.TABLE_ITEM,
    }

    if asset_field in parent_fields:
        return await _generate_parent_asset_name(asset_type, inventory)
    elif asset_field in child_fields:
        return await _generate_child_asset_name(asset_type, parent_asset_name)
    else:
        raise ValueError(f"Unsupported asset field: {asset_field}")


async def generate_data_choice(
    canarydrop: Canarydrop,
    asset_type: AWSInfraAssetType,
    asset_field: str,
    parent_asset_name: str = None,
) -> str:
    """Generate a random data choice for the given asset type and field."""
    inventory = _get_inventory_for_asset_type(canarydrop, asset_type)

    return await _generate_asset_by_type_and_field(
        asset_type, asset_field, inventory, parent_asset_name
    )


async def generate_child_assets(assets: dict):
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
                NAME_GENERATOR.generate_children_names(
                    asset_type, asset_name, random.randint(1, MAX_CHILD_ITEMS)
                )
            )
    all_names = await asyncio.gather(*tasks)

    i = 0
    for asset_type, asset_names in assets.items():
        for asset_name in asset_names:
            result[asset_type][asset_name] = all_names[i]
            i += 1

    return result
