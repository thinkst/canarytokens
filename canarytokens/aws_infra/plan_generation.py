import json
import random
import string

from canarytokens.aws_infra.db_queries import get_current_assets
from canarytokens.aws_infra.data_generation import GeminiDecoyNameGenerator
from canarytokens.aws_infra.state_management import is_ingesting
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetType
from canarytokens.settings import FrontendSettings

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


def generate_s3_buckets(inventory: list, count: int = 1):
    """
    Return a name for a S3 bucket.
    """
    suggested = NAME_GENERATOR.generate_names(
        AWSInfraAssetType.S3_BUCKET, inventory, count
    )
    return suggested.suggested_names


def generate_s3_object():
    """
    Return a path for a S3 object.
    """
    objects = ["object", "data", "text", "passwords"]
    directory = "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(10)]
    )
    return f"{random.randint(2000, 2025)}/{directory}/{random.choice(objects)}"


def generate_sqs_queue():
    """
    Return a name for a SQS queue.
    """
    separator = random.choice(["", "-", "_"])

    return f"{separator.join([random.choice(s) for s in [NAME_ENVS, NAME_TARGETS]])}{separator}"


def generate_ssm_parameter():
    separator = random.choice(["", "-", "_"])
    return f"{separator.join([random.choice(s) for s in [NAME_ENVS, NAME_TARGETS]])}{separator}"


def generate_secretsmanager_secret():
    """
    Return a name for a Secrets Manager secret.
    """
    separator = random.choice(["", "-", "_", "+", "=", "@"])
    return f"{separator.join([random.choice(s) for s in [NAME_ENVS, NAME_TARGETS]])}{separator}"


def generate_dynamo_table():
    """
    Return a name for a DynamoDB table.
    """
    separator = random.choice(["", "-", "_"])
    return f"{separator.join([random.choice(s) for s in [NAME_ENVS, NAME_TARGETS]])}{separator}"


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


def add_new_assets_to_plan(
    aws_deployed_assets: dict, aws_inventoried_assets: dict, plan: dict
):
    # generate new assets
    count = random.randint(
        1,
        MAX_S3_BUCKETS
        - len(aws_deployed_assets.get(AWSInfraAssetType.S3_BUCKET.value, [])),
    )

    plan["assets"][AWSInfraAssetType.S3_BUCKET.value].extend(
        [
            {"bucket_name": bucket_name, "objects": [], "off_inventory": False}
            for bucket_name in generate_s3_buckets(
                aws_inventoried_assets.get(AWSInfraAssetType.S3_BUCKET.value, []), count
            )
        ]
    )
    for i in range(len(plan["assets"][AWSInfraAssetType.S3_BUCKET.value])):
        for _ in range(random.randint(1, MAX_S3_OBJECTS)):
            plan["assets"][AWSInfraAssetType.S3_BUCKET.value][i]["objects"].append(
                {"object_path": generate_s3_object()}
            )

    for i in range(
        random.randint(
            1,
            MAX_SQS_QUEUES
            - len(aws_deployed_assets.get(AWSInfraAssetType.SQS_QUEUE.value, [])),
        )
    ):
        plan["assets"][AWSInfraAssetType.SQS_QUEUE.value].append(
            {"sqs_queue_name": generate_sqs_queue(), "off_inventory": False}
        )

    for i in range(
        random.randint(
            1,
            MAX_SSM_PARAMETERS
            - len(aws_deployed_assets.get(AWSInfraAssetType.SSM_PARAMETER.value, [])),
        )
    ):
        plan["assets"][AWSInfraAssetType.SSM_PARAMETER.value].append(
            {"ssm_parameter_name": generate_ssm_parameter(), "off_inventory": False}
        )

    for i in range(
        random.randint(
            1,
            MAX_SECRET_MANAGER_SECRETS
            - len(
                aws_deployed_assets.get(
                    AWSInfraAssetType.SECRETS_MANAGER_SECRET.value, []
                )
            ),
        )
    ):
        plan["assets"][AWSInfraAssetType.SECRETS_MANAGER_SECRET.value].append(
            {"secret_name": generate_secretsmanager_secret(), "off_inventory": False}
        )

    for i in range(
        random.randint(
            1,
            MAX_DYNAMO_TABLES
            - len(aws_deployed_assets.get(AWSInfraAssetType.DYNAMO_DB_TABLE.value, [])),
        )
    ):
        plan["assets"][AWSInfraAssetType.DYNAMO_DB_TABLE.value].append(
            {
                "table_name": generate_dynamo_table(),
                "off_inventory": False,
                "table_items": [],
            }
        )
        for _ in range(random.randint(1, MAX_DYNAMO_TABLES_ITEMS)):
            plan["assets"][AWSInfraAssetType.DYNAMO_DB_TABLE.value][i][
                "table_items"
            ].append(generate_dynamo_table_item())


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

    add_new_assets_to_plan(aws_deployed_assets, aws_inventoried_assets, proposed_plan)
    if is_ingesting(canarydrop):
        return proposed_plan

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
        (AWSInfraAssetType.S3_BUCKET, "bucket_name"): generate_s3_buckets,
        (AWSInfraAssetType.S3_BUCKET, "object_path"): generate_s3_object,
        (AWSInfraAssetType.SQS_QUEUE, "queue_name"): generate_sqs_queue,
        (AWSInfraAssetType.SQS_QUEUE, "message_count"): lambda: str(
            random.randint(0, 10)
        ),
        (AWSInfraAssetType.SSM_PARAMETER, "parameter_name"): generate_ssm_parameter,
        (
            AWSInfraAssetType.SECRETS_MANAGER_SECRET,
            "secretsmanager_secret_name",
        ): generate_secretsmanager_secret,
        (
            AWSInfraAssetType.SECRETS_MANAGER_SECRET,
            "secretsmanager_secret_value",
        ): lambda: "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(random.randint(5, 50))
        ),
        (AWSInfraAssetType.DYNAMO_DB_TABLE, "dynamodb_name"): generate_dynamo_table,
        (AWSInfraAssetType.DYNAMO_DB_TABLE, "dynamodb_partition_key"): lambda: "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(random.randint(3, 10))
        ),
        (AWSInfraAssetType.DYNAMO_DB_TABLE, "dynamodb_row_count"): lambda: str(
            random.randint(0, 100)
        ),
    }

    # Retrieve the corresponding function or value
    _generate_data_choice = asset_map.get((asset_type, asset_field))
    if _generate_data_choice:
        return _generate_data_choice()

    raise ValueError(
        f"Invalid asset type and asset field pairing: {asset_type}, {asset_field}"
    )
