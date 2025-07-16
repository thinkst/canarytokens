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
MAX_S3_OBJECTS = 100
MAX_S3_BUCKETS = 10
MAX_DYNAMO_TABLES = 10
MAX_DYNAMO_TABLES_ITEMS = 100
MAX_SSM_PARAMETERS = 10
MAX_SQS_QUEUES = 10
MAX_SECRET_MANAGER_SECRETS = 10

NAME_GENERATOR = GeminiDecoyNameGenerator()


def generate_tf_variables(canarydrop: Canarydrop, plan):
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
        tf_variables["s3_bucket_names"].append(bucket["bucket_name"])
        for s3_object in bucket["objects"]:
            tf_variables["s3_objects"].append(
                {
                    "bucket": bucket["bucket_name"],
                    "key": s3_object["object_path"],
                    "content": "".join(
                        [
                            random.choice(string.ascii_letters + string.digits)
                            for _ in range(random.randint(5, 1000))
                        ]
                    ),
                }
            )
    return tf_variables


def generate_s3_object():
    """
    Return a path for a S3 object.
    """
    objects = ["object", "data", "text", "passwords"]
    directory = "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(10)]
    )
    return f"{random.randint(2000, 2025)}/{directory}/{random.choice(objects)}"


async def generate_for_asset_type(
    asset_type: AWSInfraAssetType, inventory: list, count: int = 1
):
    suggested = await NAME_GENERATOR.generate_names(asset_type, inventory, count)
    return suggested.suggested_names


def generate_dynamo_table_item():
    """
    Return a name for a DynamoDB table item.
    """
    separator = random.choice(["", "-", "_"])
    items = ["object", "data", "text", "passwords"]
    suffix = "".join(
        [random.choice(string.ascii_lowercase + string.digits) for _ in range(5)]
    )
    return f"{random.choice(items)}{separator}{suffix}"


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
            {"bucket_name": bucket_name, "objects": [], "off_inventory": False}
            for bucket_name in bucket_names
        ]
    )
    for i in range(len(plan["assets"][AWSInfraAssetType.S3_BUCKET.value])):
        for _ in range(random.randint(1, MAX_S3_OBJECTS)):
            plan["assets"][AWSInfraAssetType.S3_BUCKET.value][i]["objects"].append(
                {"object_path": generate_s3_object()}
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
            {"sqs_queue_name": sqs_queue_name, "off_inventory": False}
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
            {"ssm_parameter_name": ssm_parameter_name, "off_inventory": False}
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
            {"secret_name": secret_name, "off_inventory": False}
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
            {"table_name": table_name, "off_inventory": False, "table_items": []}
            for table_name in table_names
        ]
    )
    for i in range(len(plan["assets"][AWSInfraAssetType.DYNAMO_DB_TABLE.value])):
        for _ in range(random.randint(1, MAX_DYNAMO_TABLES_ITEMS)):
            plan["assets"][AWSInfraAssetType.DYNAMO_DB_TABLE.value][i][
                "table_items"
            ].append(generate_dynamo_table_item())


def _get_decoy_asset_count(
    aws_inventoried_assets,
    asset_type: AWSInfraAssetType,
    aws_deployed_assets,
    MAX_ASSETS: int,
):
    return min(
        math.ceil(len(aws_inventoried_assets.get(asset_type.value, [])) * 1),
        MAX_ASSETS - len(aws_deployed_assets.get(asset_type.value, [])),
    )


async def add_new_assets_to_plan(
    aws_deployed_assets: dict, aws_inventoried_assets: dict, plan: dict
):
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
                lambda bucket: bucket["bucket_name"] == bucket_name,
                current_plan.get("assets", {}).get(
                    AWSInfraAssetType.S3_BUCKET.value, []
                ),
            )
        )[0].get("objects", [])
        proposed_plan["assets"][AWSInfraAssetType.S3_BUCKET.value].append(
            {
                "bucket_name": bucket_name,
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
                "sqs_queue_name": sqs_queue_name,
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
                "ssm_parameter_name": ssm_parameter_name,
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
                "secret_name": secret_name,
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
                lambda table: table["table_name"] == table_name,
                current_plan.get("assets", {}).get(
                    AWSInfraAssetType.DYNAMO_DB_TABLE.value, []
                ),
            )
        )[0].get("table_items", [])
        proposed_plan["assets"][AWSInfraAssetType.DYNAMO_DB_TABLE.value].append(
            {
                "table_name": table_name,
                "off_inventory": table_name
                not in aws_inventoried_assets.get(
                    AWSInfraAssetType.DYNAMO_DB_TABLE.value, []
                ),
                "table_items": table_items,
            }
        )


def generate_proposed_plan(canarydrop: Canarydrop):
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

    add_new_assets_to_plan(aws_deployed_assets, aws_inventoried_assets, proposed_plan)
    add_current_assets_to_plan(
        aws_deployed_assets, aws_inventoried_assets, proposed_plan, current_plan
    )
    return proposed_plan


def _get_ingestion_bus_arn(bus_name: str):
    return f"arn:aws:events:eu-west-1:{settings.AWS_INFRA_AWS_ACCOUNT}:event-bus/{bus_name}"


def generate_data_choice(asset_type: AWSInfraAssetType, asset_field: str):
    """
    Generate a random data choice for the given asset type and field.
    """
    asset_map = {
        # (AWSInfraAssetType.S3_BUCKET, "bucket_name"): generate_s3_buckets,
        # (AWSInfraAssetType.S3_BUCKET, "object_path"): generate_s3_object,
        # (AWSInfraAssetType.SQS_QUEUE, "queue_name"): generate_sqs_queue,
        # (AWSInfraAssetType.SQS_QUEUE, "message_count"): lambda: str(
        #     random.randint(0, 10)
        # ),
        # (AWSInfraAssetType.SSM_PARAMETER, "parameter_name"): generate_ssm_parameters,
        # (
        #     AWSInfraAssetType.SECRETS_MANAGER_SECRET,
        #     "secretsmanager_secret_name",
        # ): generate_secretsmanager_secrets,
        # (
        #     AWSInfraAssetType.SECRETS_MANAGER_SECRET,
        #     "secretsmanager_secret_value",
        # ): lambda: "".join(
        #     random.choice(string.ascii_letters + string.digits)
        #     for _ in range(random.randint(5, 50))
        # ),
        # (AWSInfraAssetType.DYNAMO_DB_TABLE, "dynamodb_name"): generate_dynamo_table,
        # (AWSInfraAssetType.DYNAMO_DB_TABLE, "dynamodb_partition_key"): lambda: "".join(
        #     random.choice(string.ascii_letters + string.digits)
        #     for _ in range(random.randint(3, 10))
        # ),
        # (AWSInfraAssetType.DYNAMO_DB_TABLE, "dynamodb_row_count"): lambda: str(
        #     random.randint(0, 100)
        # ),
    }

    # Retrieve the corresponding function or value
    _generate_data_choice = asset_map.get((asset_type, asset_field))
    if _generate_data_choice:
        return _generate_data_choice()

    raise ValueError(
        f"Invalid asset type and asset field pairing: {asset_type}, {asset_field}"
    )
