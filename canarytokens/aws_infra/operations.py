from dataclasses import dataclass
from datetime import datetime, timezone
import string
import secrets
import json
from typing import Union

from canarytokens import queries
from canarytokens.aws_infra.management import (
    SQS_CLIENT,
    upload_tf_module,
)
from canarytokens.aws_infra.plan_generation import generate_tf_variables
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetType, AWSInfraOperationType
from canarytokens.settings import FrontendSettings
from canarytokens.tokens import Canarytoken

settings = FrontendSettings()

AWS_INFRA_AWS_ACCOUNT = settings.AWS_INFRA_AWS_ACCOUNT
AWS_INFRA_SHARED_SECRET = None
MANAGEMENT_REQUEST_URL = settings.AWS_INFRA_MANAGEMENT_REQUEST_SQS_URL
INVENTORY_ROLE_NAME = settings.AWS_INFRA_INVENTORY_ROLE


@dataclass
class Handle:
    response_received: bool
    response: Union[bool, str, dict]


def get_role_commands(canarydrop: Canarydrop):
    """
    Return the aws-cli commands needed to setup the inventory role in the customer's account
    """
    return {
        "role_name": settings.AWS_INFRA_INVENTORY_ROLE,
        "aws_account": AWS_INFRA_AWS_ACCOUNT,
        "external_id": canarydrop.aws_customer_iam_access_external_id,
        "customer_aws_account": canarydrop.aws_account_id,
    }


def get_role_cleanup_commands(canarydrop: Canarydrop):
    """
    Return the aws-cli commands needed to detach and delete the inventory policy and role in the customer's account
    """
    return {
        "role_name": settings.AWS_INFRA_INVENTORY_ROLE,
        "customer_aws_account": canarydrop.aws_account_id,
    }


def _generate_handle_id():
    return secrets.token_hex(20)


def create_handle(operation: AWSInfraOperationType, canarydrop: Canarydrop):
    "Create a new handle entry in the redis DB and trigger the specified operation"
    handle_id = _generate_handle_id()
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
            "bus_name": canarydrop.aws_infra_ingestion_bus_name,
            "region": canarydrop.aws_region,
            "aws_account": canarydrop.aws_account_id,
            "callback_domain": settings.DOMAINS[0],
        }

    elif operation == AWSInfraOperationType.TEARDOWN:
        payload["params"] = {
            "canarytoken_id": canarydrop.canarytoken.value(),
            "bus_name": canarydrop.aws_infra_ingestion_bus_name,
            "region": canarydrop.aws_region,
            "aws_account": canarydrop.aws_account_id,
        }
    SQS_CLIENT.send_message(
        QueueUrl=MANAGEMENT_REQUEST_URL, MessageBody=json.dumps(payload)
    )


# TODO: add handle exist for token validation
def get_handle_response(handle_id):
    """
    Check if a response has been added to the specified handle in the redis DB and return it.
    """
    handle = queries.get_aws_management_lambda_handle(handle_id)
    if not handle:
        raise Exception("Handle does not exist")
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
    """
    Return the operation type associated with a specific handle
    """
    handle = queries.get_aws_management_lambda_handle(handle_id)
    if handle is None:
        return None
    return handle.get("operation")


def add_handle_response(handle_id, response):
    """
    Update the specified handle with a response in the redis DB.
    """
    queries.update_aws_management_lambda_handle(handle_id, json.dumps(response))


def save_plan(canarydrop: Canarydrop, plan: str):
    """
    Save an AWS Infra plan and upload it to the tf modules S3 bucket.
    """
    # TODO: validate plan
    canarydrop.aws_saved_plan = json.dumps(plan)
    # TODO: add other asset types
    canarydrop.aws_deployed_assets = json.dumps(
        {
            AWSInfraAssetType.S3_BUCKET.value: [
                bucket["bucket_name"]
                for bucket in plan["assets"][AWSInfraAssetType.S3_BUCKET.value]
            ]
        }
    )
    queries.save_canarydrop(canarydrop)
    variables = generate_tf_variables(canarydrop, plan)
    upload_tf_module(
        canarydrop.canarytoken.value(), canarydrop.aws_tf_module_prefix, variables
    )


def save_current_assets(canarydrop: Canarydrop, assets: dict):
    canarydrop.aws_inventoried_assets = json.dumps(assets)
    queries.save_canarydrop(canarydrop)


def get_canarydrop_from_handle(handle_id: str):
    return queries.get_canarydrop(
        Canarytoken(
            value=queries.get_aws_management_lambda_handle(handle_id).get("canarytoken")
        )
    )


def get_module_snippet(canarydrop: Canarydrop):
    """
    Return the snippet that can be pasted in the customer's terraform.
    """

    return f'module "canarytoken_infra" {{ source = "https://{settings.AWS_INFRA_TF_MODULE_BUCKET}.s3.eu-west-1.amazonaws.com/{canarydrop.aws_tf_module_prefix}/{canarydrop.canarytoken.value()}/tf.zip" }}'


def generate_external_id():
    return "".join(
        [secrets.choice(string.ascii_letters + string.digits) for _ in range(21)]
    )
