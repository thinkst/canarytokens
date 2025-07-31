import enum

from canarytokens.aws_infra.utils import generate_content
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetField, AWSInfraAssetType
from canarytokens.settings import FrontendSettings

settings = FrontendSettings()


class Variable(str, enum.Enum):
    S3_BUCKET_NAMES = "s3_bucket_names"
    S3_OBJECTS = "s3_objects"
    SQS_QUEUES = "sqs_queues"
    SSM_PARAMETERS = "ssm_parameters"
    SECRETS = "secrets"
    TABLES = "tables"
    TABLE_ITEMS = "table_items"
    CANARYTOKEN_ID = "canarytoken_id"
    TARGET_BUS_ARN = "target_bus_arn"
    ACCOUNT_ID = "account_id"
    REGION = "region"


def generate_tf_variables(canarydrop: Canarydrop, plan: dict) -> dict:
    """
    Generate variables to be used in the terraform template.
    """
    tf_variables = {
        Variable.S3_BUCKET_NAMES: [],
        Variable.S3_OBJECTS: [],
        Variable.SQS_QUEUES: [],
        Variable.SSM_PARAMETERS: [],
        Variable.SECRETS: [],
        Variable.TABLES: [],
        Variable.TABLE_ITEMS: [],
        Variable.CANARYTOKEN_ID: canarydrop.canarytoken.value(),
        Variable.TARGET_BUS_ARN: f"arn:aws:events:eu-west-1:{settings.AWS_INFRA_AWS_ACCOUNT}:event-bus/{canarydrop.aws_infra_ingestion_bus_name}",
        Variable.ACCOUNT_ID: canarydrop.aws_account_id,
        Variable.REGION: canarydrop.aws_region,
    }

    _add_s3_buckets(tf_variables, plan)
    _add_sqs_queues(tf_variables, plan)
    _add_ssm_parameters(tf_variables, plan)
    _add_secrets(tf_variables, plan)
    _add_dynamodb_tables(tf_variables, plan)

    return tf_variables


def _add_s3_buckets(tf_variables, plan):
    for bucket in plan.get(AWSInfraAssetType.S3_BUCKET, []):
        tf_variables[Variable.S3_BUCKET_NAMES].append(
            bucket[AWSInfraAssetField.BUCKET_NAME]
        )
        for s3_object in bucket.get("objects", []):
            tf_variables[Variable.S3_OBJECTS].append(
                {
                    "bucket": bucket[AWSInfraAssetField.BUCKET_NAME],
                    "key": s3_object,
                    "content": generate_content(),
                }
            )


def _add_sqs_queues(tf_variables, plan):
    for queue in plan.get(AWSInfraAssetType.SQS_QUEUE, []):
        tf_variables[Variable.SQS_QUEUES].append(
            queue[AWSInfraAssetField.SQS_QUEUE_NAME]
        )


def _add_ssm_parameters(tf_variables, plan):
    for param in plan.get(AWSInfraAssetType.SSM_PARAMETER, []):
        tf_variables[Variable.SSM_PARAMETERS].append(
            {
                "name": param[AWSInfraAssetField.SSM_PARAMETER_NAME],
                "value": generate_content(),
            }
        )


def _add_secrets(tf_variables, plan):
    for secret in plan.get(AWSInfraAssetType.SECRETS_MANAGER_SECRET, []):
        tf_variables[Variable.SECRETS].append(
            secret[AWSInfraAssetField.SECRET_NAME],
        )


def _add_dynamodb_tables(tf_variables, plan):
    for table in plan.get(AWSInfraAssetType.DYNAMO_DB_TABLE, []):
        tf_variables[Variable.TABLES].append(table[AWSInfraAssetField.TABLE_NAME])
        for item in table.get("table_items", []):
            tf_variables[Variable.TABLE_ITEMS].append(
                {
                    "table_name": table[AWSInfraAssetField.TABLE_NAME],
                    "key": "id",
                    "value": item,  # Assuming 'id' is the primary key
                }
            )
