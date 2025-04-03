from dataclasses import dataclass
from datetime import datetime, timezone
import string
import secrets
import json
import boto3

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetType, AWSInfraOperationType
from canarytokens.settings import FrontendSettings


settings = FrontendSettings()

MANAGEMENT_REQUEST_URL = settings.AWS_INFRA_MANAGEMENT_REQUEST_SQS_URL
INVENTORY_ROLE_NAME = settings.AWS_INFRA_INVENTORY_ROLE
MANAGEMENT_REQUEST_SQS_CLIENT = None


@dataclass
class Handle:
    response_received: bool
    response: bool | str | dict


def get_sqs_client():
    global MANAGEMENT_REQUEST_SQS_CLIENT
    if MANAGEMENT_REQUEST_SQS_CLIENT is None:
        MANAGEMENT_REQUEST_SQS_CLIENT = boto3.client(
            "sqs",
            region_name="eu-west-1",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
        )

    return MANAGEMENT_REQUEST_SQS_CLIENT


def generate_external_id():
    return "".join(
        [secrets.choice(string.ascii_letters + string.digits) for _ in range(21)]
    )


ROLE_SETUP_COMMNANDS_TEMPLATE = [
    'aws iam create-role --role-name $role_name --assume-role-policy-document \'{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Principal": {"AWS": "arn:aws:iam::$aws_account:role/lambda-Canarytokens-Inventory-Manager"},"Action": "sts:AssumeRole","Condition": {"StringEquals": {"sts:ExternalId": "$external_id"}}}]}\'',
    'aws iam create-policy --policy-nameCanarytokens-Inventory-ReadOnly-Policy --policy-document \'{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Action": ["sqs:ListQueues","sqs:GetQueueAttributes],"Resource": "*"},{"Effect": "Allow","Action": ["s3:ListAllMyBuckets"],"Resource": "*"}]}\'',
    "aws iam attach-role-policy --role-name $role_name --policy-arn arn:aws:iam::$customer_aws_account:policy/Canarytokens-Inventory-ReadOnly-Policy",
]


def get_role_commands(canarydrop: Canarydrop):
    return [
        string.Template(role_command)
        .safe_substitute(
            role_name=settings.AWS_INFRA_INVENTORY_ROLE,
            aws_account=settings.AWS_INFRA_AWS_ACCOUNT,
            external_id=canarydrop.aws_customer_iam_access_external_id,
            customer_aws_account=canarydrop.aws_account_id,
        )
        .replace("\n", "")
        for role_command in ROLE_SETUP_COMMNANDS_TEMPLATE
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

    if (
        operation == AWSInfraOperationType.CHECK_ROLE
        or operation == AWSInfraOperationType.INVENTORY
    ):
        payload["params"] = {
            "aws_account": canarydrop.aws_account_id,
            "customer_iam_access_external_id": canarydrop.aws_customer_iam_access_external_id,
            "role_name": INVENTORY_ROLE_NAME,
        }
    if operation == AWSInfraOperationType.INVENTORY:
        payload["params"] = {
            "region": canarydrop.aws_region,
            "asset_types": [asset_type.value for asset_type in AWSInfraAssetType],
        }

    if (
        operation == AWSInfraOperationType.SETUP_INGESTION
        or operation == AWSInfraOperationType.TEARDOWN
    ):
        payload["params"] = {
            "canarytoken_id": canarydrop.canarytoken.value(),
            "customer_cloudtrail_arn": None,
            "alert_ingestion_bucket": None,
        }

    if operation == AWSInfraOperationType.SETUP_INGESTION or operation:
        payload["params"] = {
            "callback_domain": settings.AWS_INFRA_CALLBACK_DOMAIN,
        }

    response = get_sqs_client().send_message(
        QueueUrl=MANAGEMENT_REQUEST_URL, MessageBody=json.dumps(payload)
    )
    print(response)


def get_handle_response(handle_id):
    handle = queries.get_aws_management_lambda_handle(handle_id)
    response = json.loads(handle.get("response_content"))
    if handle.get("response_received") == "True":
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
