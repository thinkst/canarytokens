from dataclasses import dataclass
from datetime import datetime, timezone
import shutil
import string
import secrets
import json
from typing import Union
import boto3
import os

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetType, AWSInfraOperationType
from canarytokens.settings import FrontendSettings


settings = FrontendSettings()

MANAGEMENT_REQUEST_URL = settings.AWS_INFRA_MANAGEMENT_REQUEST_SQS_URL
INVENTORY_ROLE_NAME = settings.AWS_INFRA_INVENTORY_ROLE


@dataclass
class Handle:
    response_received: bool
    response: Union[bool, str, dict]


def get_session():
    os.environ["AWS_CONFIG_FILE"] = "/dev/null"
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "/dev/null"
    return boto3.Session()


def get_sqs_client():
    return get_session().client(
        "sqs",
        region_name="eu-west-1",
        # aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        # aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        # aws_session_token=settings.AWS_SESSION_TOKEN,
    )


def generate_external_id():
    return "".join(
        [secrets.choice(string.ascii_letters + string.digits) for _ in range(21)]
    )


ROLE_SETUP_COMMANDS_TEMPLATE = [
    """
    aws iam create-role --role-name $role_name --assume-role-policy-document
    \'{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:sts::$aws_account:assumed-role/InventoryManagerRole/$external_id"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "$external_id"
                }
            }
        }
    ]
    }\'
    """,
    'aws iam create-policy --policy-name Canarytokens-Inventory-ReadOnly-Policy --policy-document \'{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Action": ["sqs:ListQueues","sqs:GetQueueAttributes"],"Resource": "*"},{"Effect": "Allow","Action": ["s3:ListAllMyBuckets"],"Resource": "*"}]}\'',
    "aws iam attach-role-policy --role-name $role_name --policy-arn arn:aws:iam::$customer_aws_account:policy/Canarytokens-Inventory-ReadOnly-Policy",
]


def get_role_commands(canarydrop: Canarydrop):
    return [
        " ".join(
            string.Template(role_command)
            .safe_substitute(
                role_name=settings.AWS_INFRA_INVENTORY_ROLE,
                aws_account=settings.AWS_INFRA_AWS_ACCOUNT,
                external_id=canarydrop.aws_customer_iam_access_external_id,
                customer_aws_account=canarydrop.aws_account_id,
            )
            .split()
        )
        for role_command in ROLE_SETUP_COMMANDS_TEMPLATE
    ]


def generate_handle_id():
    return secrets.token_hex(20)


def create_handle(operation: AWSInfraOperationType, canarydrop: Canarydrop):
    handle_id = generate_handle_id()
    queries.add_aws_management_lambda_handle(
        handle_id, canarydrop.canarytoken.value(), operation
    )
    trigger_operation(operation, handle_id, canarydrop)
    return handle_id


def trigger_operation(operation: AWSInfraOperationType, handle, canarydrop: Canarydrop):
    payload = {
        "handle": handle,
        "operation": operation.value,
    }

    if operation == AWSInfraOperationType.CHECK_ROLE:
        payload["params"] = {
            "aws_account": canarydrop.aws_account_id,
            "customer_iam_access_external_id": canarydrop.aws_customer_iam_access_external_id,
            "role_name": INVENTORY_ROLE_NAME,
        }
    elif operation == AWSInfraOperationType.INVENTORY:
        payload["params"] = {
            "aws_account": canarydrop.aws_account_id,
            "customer_iam_access_external_id": canarydrop.aws_customer_iam_access_external_id,
            "role_name": INVENTORY_ROLE_NAME,
            "region": canarydrop.aws_region,
            "assets_types": [asset_type.value for asset_type in AWSInfraAssetType],
        }

    elif operation == AWSInfraOperationType.SETUP_INGESTION:
        payload["params"] = {
            "canarytoken_id": canarydrop.canarytoken.value(),
            "customer_cloudtrail_arn": f"arn:aws:cloudtrail:{canarydrop.aws_region}:{canarydrop.aws_account_id}:trail/{canarydrop.aws_infra_cloudtrail_name}",
            "alert_ingestion_bucket": settings.AWS_INFRA_CLOUDTRAIL_BUCKET,
            "callback_domain": settings.DOMAINS[0],
        }

    elif operation == AWSInfraOperationType.TEARDOWN:
        payload["params"] = {
            "canarytoken_id": canarydrop.canarytoken.value(),
            "customer_cloudtrail_arn": f"arn:aws:cloudtrail:{canarydrop.aws_region}:{canarydrop.aws_account_id}:trail/{canarydrop.aws_infra_cloudtrail_name}",
            "alert_ingestion_bucket": settings.AWS_INFRA_CLOUDTRAIL_BUCKET,
        }
    print(payload)
    response = get_sqs_client().send_message(
        QueueUrl=MANAGEMENT_REQUEST_URL, MessageBody=json.dumps(payload)
    )
    print(response)


def get_handle_response(handle_id):
    handle = queries.get_aws_management_lambda_handle(handle_id)
    if handle.get("response_received") == "True":
        response = json.loads(handle.get("response_content"))
        return Handle(response_received=True, response=response)
    requested_time = datetime.strptime(
        handle.get("requested_timestamp"), "%Y-%m-%d %H:%M:%S"
    ).timestamp()
    current_time = datetime.now(timezone.utc).timestamp()
    if requested_time - current_time > 300:
        return Handle(response_received=True, response="")
    return Handle(response_received=False, response="")


def get_handle_operation(handle_id):
    handle = queries.get_aws_management_lambda_handle(handle_id)
    if handle is None:
        return None
    return handle.get("operation")


def add_handle_response(handle_id, response):
    queries.update_aws_management_lambda_handle(handle_id, json.dumps(response))


def save_plan(canarydrop: Canarydrop, plan: str):
    # TODO: validate plan
    canarydrop.aws_saved_plan = plan
    #  queries.save_canarydrop(canarydrop)
    variables = generate_tf_variables(canarydrop, plan)
    upload_zip(
        canarydrop.canarytoken.value(), canarydrop.aws_tf_module_prefix, variables
    )
    return f"s3::https://{settings.AWS_INFRA_TF_MODULE_BUCKET}.s3.eu-west-1.amazonaws.com/{canarydrop.aws_tf_module_prefix}/{canarydrop.canarytoken.value()}/tf.zip"


def generate_tf_variables(canarydrop: Canarydrop, plan):
    tf_variables = {
        "s3_bucket_names": [],
        "s3_objects": [],
        "canarytoken_id": canarydrop.canarytoken.value(),
        "cloudtrail_name": canarydrop.aws_infra_cloudtrail_name,
        "cloudtrail_destination_bucket": settings.AWS_INFRA_CLOUDTRAIL_BUCKET,
    }
    for bucket in plan["assets"]["S3Bucket"]:
        tf_variables["s3_bucket_names"].append(bucket["bucket_name"])
        for s3_object in bucket["objects"]:
            tf_variables["s3_objects"].append(
                {
                    "bucket": bucket["bucket_name"],
                    "key": s3_object["object_path"],
                    "content": s3_object["content"],
                }
            )
    return tf_variables


def upload_zip(canarytoken_id, prefix, variables):
    new_dir = shutil.copytree("../aws_ct_tf", f"aws_ct_tf_{canarytoken_id}")
    with open(f"{new_dir}/decoy_vars.json", "w") as f:
        f.write(json.dumps(variables))

    archive = shutil.make_archive(f"module_tf_{canarytoken_id}", "zip", new_dir)
    s3 = get_session().resource(
        "s3",
        region_name="eu-west-1",
        # aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        # aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        # aws_session_token=settings.AWS_SESSION_TOKEN,
    )
    s3.Bucket(settings.AWS_INFRA_TF_MODULE_BUCKET).upload_file(
        archive, f"{prefix}/{canarytoken_id}/tf.zip"
    )
    shutil.rmtree(new_dir)
    os.remove(archive)


def generate_cloudtrail_name():
    return f"trail-{''.join([secrets.choice(string.ascii_letters + string.digits) for _ in range(21)])}"
