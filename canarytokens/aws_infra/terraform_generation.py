import enum
import random

from canarytokens.aws_infra.aws_management import upload_tf_module
from canarytokens.aws_infra.plan_generation import AssetLabel, _get_ingestion_bus_arn
from canarytokens.aws_infra.utils import random_string
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetType, TokenTypes
from canarytokens.tokens import Canarytoken


class Variable(str, enum.Enum):
    S3_BUCKET_NAME = "s3_bucket_name"
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
        Variable.S3_BUCKET_NAME: [],
        Variable.S3_OBJECTS: [],
        Variable.SQS_QUEUES: [],
        Variable.SSM_PARAMETERS: [],
        Variable.SECRETS: [],
        Variable.TABLES: [],
        Variable.TABLE_ITEMS: [],
        Variable.CANARYTOKEN_ID: canarydrop.canarytoken.value(),
        Variable.TARGET_BUS_ARN: _get_ingestion_bus_arn(
            canarydrop.aws_infra_ingestion_bus_name
        ),
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
    for bucket in plan["assets"].get("S3Bucket", []):
        tf_variables[Variable.S3_BUCKET_NAME].append(bucket[AssetLabel.BUCKET_NAME])
        for s3_object in bucket.get("objects", []):
            tf_variables[Variable.S3_OBJECTS].append(
                {
                    "bucket": bucket[AssetLabel.BUCKET_NAME],
                    "key": s3_object,
                    "content": random_string(
                        random.randint(5, 1000)
                    ),  # Random content for the object
                }
            )


def _add_sqs_queues(tf_variables, plan):
    for queue in plan["assets"].get("SQSQueue", []):
        tf_variables[Variable.SQS_QUEUES].append(queue[AssetLabel.SQS_QUEUE_NAME])


def _add_ssm_parameters(tf_variables, plan):
    for param in plan["assets"].get("SSMParameter", []):
        tf_variables[Variable.SSM_PARAMETERS].append(
            {
                "name": param[AssetLabel.SSM_PARAMETER_NAME],
                "value": random_string(random.randint(5, 1000)),
            }
        )


def _add_secrets(tf_variables, plan):
    for secret in plan["assets"].get("SecretsManagerSecret", []):
        tf_variables[Variable.SECRETS].append(
            secret[AssetLabel.SECRET_NAME],
        )


def _add_dynamodb_tables(tf_variables, plan):
    for table in plan["assets"].get("DynamoDBTable", []):
        tf_variables[Variable.TABLES].append(table[AssetLabel.TABLE_NAME])
        for item in table.get("table_items", []):
            tf_variables[Variable.TABLE_ITEMS].append(
                {
                    "table_name": table[AssetLabel.TABLE_NAME],
                    "key": item,
                    "value": random_string(random.randint(5, 1000)),
                }
            )


if __name__ == "__main__":
    # Example usage or test code can go here
    plan = {
        "assets": {
            AWSInfraAssetType.S3_BUCKET: [
                {
                    AssetLabel.BUCKET_NAME: "bucket1",
                    AssetLabel.OBJECTS: ["file1.txt", "file2.txt"],
                },
                {
                    AssetLabel.BUCKET_NAME: "bucket2",
                    AssetLabel.OBJECTS: ["file3.txt", "file4.txt"],
                },
            ],
            AWSInfraAssetType.SQS_QUEUE: [
                {AssetLabel.SQS_QUEUE_NAME: "queue1"},
                {AssetLabel.SQS_QUEUE_NAME: "queue2"},
            ],
            AWSInfraAssetType.SSM_PARAMETER: [
                {AssetLabel.SSM_PARAMETER_NAME: "pa/ram/1"},
                {AssetLabel.SSM_PARAMETER_NAME: "pa/ram/2"},
            ],
            AWSInfraAssetType.SECRETS_MANAGER_SECRET: [
                {AssetLabel.SECRET_NAME: "secret1"},
                {AssetLabel.SECRET_NAME: "secret2"},
                {AssetLabel.SECRET_NAME: "secret3"},
                {AssetLabel.SECRET_NAME: "secret4"},
            ],
            AWSInfraAssetType.DYNAMO_DB_TABLE: [
                {
                    AssetLabel.TABLE_NAME: "example-table",
                    AssetLabel.TABLE_ITEMS: ["table1", "table2"],
                },
                {
                    AssetLabel.TABLE_NAME: "another-table",
                    AssetLabel.TABLE_ITEMS: ["table3", "table4"],
                },
            ],
        }
    }

    canarydrop = Canarydrop(
        type=TokenTypes.AWS_INFRA,
        canarytoken=Canarytoken(),
        aws_infra_ingestion_bus_name="trail-events-ingestion-bus-2a196c471ca955d2",
        aws_account_id="507518642175",
        aws_region="eu-west-1",
    )

    variables = generate_tf_variables(canarydrop, plan)
    print("Generated Terraform variables:")
    for key, value in variables.items():
        print(f"{key}: {value}")

    upload_tf_module(
        canarytoken_id=canarydrop.canarytoken.value(),
        prefix="test_prefix_1234",
        variables=variables,
    )
