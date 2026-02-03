import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum  # Python 3.11+
else:
    from backports.strenum import StrEnum  # Python < 3.11

from canarytokens.aws_infra.utils import generate_content
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetField, AWSInfraAssetType
from canarytokens.settings import FrontendSettings

settings = FrontendSettings()


class Variable(StrEnum):
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

    bucket_names = []
    objects = []
    for bucket in plan.get(AWSInfraAssetType.S3_BUCKET, []):
        bucket_names.append(bucket[AWSInfraAssetField.BUCKET_NAME])
        for s3_object in bucket.get("objects", []):
            objects.append(
                {
                    "bucket": bucket[AWSInfraAssetField.BUCKET_NAME],
                    "key": s3_object,
                    "content": generate_content(),
                }
            )

    queue_names = []
    for queue in plan.get(AWSInfraAssetType.SQS_QUEUE, []):
        queue_names.append(queue[AWSInfraAssetField.SQS_QUEUE_NAME])

    ssm_parameters = []
    for param in plan.get(AWSInfraAssetType.SSM_PARAMETER, []):
        ssm_parameters.append(
            {
                "name": param[AWSInfraAssetField.SSM_PARAMETER_NAME],
                "value": generate_content(),
            }
        )

    secrets = []
    for secret in plan.get(AWSInfraAssetType.SECRETS_MANAGER_SECRET, []):
        secrets.append(
            secret[AWSInfraAssetField.SECRET_NAME],
        )

    table_names = []
    table_items = []
    for table in plan.get(AWSInfraAssetType.DYNAMO_DB_TABLE, []):
        table_names.append(table[AWSInfraAssetField.TABLE_NAME])
        for item in table.get("table_items", []):
            table_items.append(
                {
                    "table_name": table[AWSInfraAssetField.TABLE_NAME],
                    "key": "id",
                    "value": item,  # Assuming 'id' is the primary key
                }
            )

    return {
        Variable.S3_BUCKET_NAMES: bucket_names,
        Variable.S3_OBJECTS: objects,
        Variable.SQS_QUEUES: queue_names,
        Variable.SSM_PARAMETERS: ssm_parameters,
        Variable.SECRETS: secrets,
        Variable.TABLES: table_names,
        Variable.TABLE_ITEMS: table_items,
        Variable.CANARYTOKEN_ID: canarydrop.canarytoken.value(),
        Variable.TARGET_BUS_ARN: f"arn:aws:events:{settings.AWS_INFRA_AWS_REGION}:{settings.AWS_INFRA_AWS_ACCOUNT}:event-bus/{canarydrop.aws_infra_ingestion_bus_name}",
        Variable.ACCOUNT_ID: canarydrop.aws_account_id,
        Variable.REGION: canarydrop.aws_region,
    }
