from datetime import datetime, timezone
import json
import logging

from pydantic import BaseModel

from canarytokens import queries
from canarytokens.aws_infra.aws_management import (
    queue_management_request,
)
from canarytokens.aws_infra.plan_generation import (
    generate_proposed_plan,
)
from canarytokens.aws_infra.state_management import is_ingesting
from canarytokens.aws_infra.utils import generate_handle_id
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import (
    AWSInfraCheckRoleReceivedResponse,
    AWSInfraHandleResponse,
    AWSInfraAssetType,
    AWSInfraInventoryCustomerAccountReceivedResponse,
    AWSInfraOperationType,
    AWSInfraServiceError,
    AWSInfraSetupIngestionReceivedResponse,
    AWSInfraTeardownReceivedResponse,
)
from canarytokens.settings import FrontendSettings
from canarytokens.tokens import Canarytoken

from canarytokens.aws_infra.db_queries import delete_current_assets, save_current_assets

settings = FrontendSettings()

AWS_INFRA_AWS_ACCOUNT = settings.AWS_INFRA_AWS_ACCOUNT
HANDLE_RESPONSE_TIMEOUT = 300  # seconds


class Handle(BaseModel):
    canarytoken: str
    operation: str
    requested_time: float
    response_received: str = "False"
    response_content: str


def get_role_create_commands(canarydrop: Canarydrop):
    """
    Return the aws-cli commands needed to setup the inventory role in the customer's account
    """
    return {
        "role_name": canarydrop.aws_infra_inventory_role,
        "aws_account": AWS_INFRA_AWS_ACCOUNT,  # TODO: rename to aws_management_account
        "external_id": canarydrop.aws_customer_iam_access_external_id,
        "customer_aws_account": canarydrop.aws_account_id,
    }


def get_role_cleanup_commands(canarydrop: Canarydrop):
    """
    Return the aws-cli commands needed to detach and delete the inventory policy and role in the customer's account
    """
    return {
        "role_name": canarydrop.aws_infra_inventory_role,
        "customer_aws_account": canarydrop.aws_account_id,
    }


def start_operation(operation: AWSInfraOperationType, canarydrop: Canarydrop):
    "Create a new handle entry in the redis DB and trigger the specified operation"
    handle_id = generate_handle_id()
    handle = Handle(
        canarytoken=canarydrop.canarytoken.value(),
        operation=operation.value,
        requested_time=datetime.now(timezone.utc).timestamp(),
        response_received="False",
        response_content="",
    )
    queries.add_aws_management_lambda_handle(
        handle_id,
        handle.dict(),
    )
    payload = _build_operation_payload(operation, handle_id, canarydrop)
    queue_management_request(payload)
    return handle_id


def _build_operation_payload(
    operation: AWSInfraOperationType, handle, canarydrop: Canarydrop
):
    """
    Construct the payload for the specified AWS infrastructure operation to be sent to the management SQS queue.
    """
    payload = {
        "handle": handle,
        "operation": operation.value,
    }

    if operation == AWSInfraOperationType.CHECK_ROLE:
        payload["params"] = {
            "aws_account": canarydrop.aws_account_id,
            "customer_iam_access_external_id": canarydrop.aws_customer_iam_access_external_id,
            "role_name": canarydrop.aws_infra_inventory_role,
        }
    elif operation == AWSInfraOperationType.INVENTORY:
        payload["params"] = {
            "aws_account": canarydrop.aws_account_id,
            "customer_iam_access_external_id": canarydrop.aws_customer_iam_access_external_id,
            "role_name": canarydrop.aws_infra_inventory_role,
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
    return payload


# TODO: add handle exist for token validation
async def get_handle_response(handle_id: str, operation: AWSInfraOperationType):
    """
    Check if a response has been added to the specified handle in the redis DB and return it.
    """
    handle = queries.get_aws_management_lambda_handle(handle_id)

    if not handle:
        logging.error(f"Handle with ID {handle_id} not found.")
        return AWSInfraHandleResponse(handle=handle_id, message="Handle not found.")

    handle = Handle(**handle)
    if handle.operation != operation.value:
        logging.error(
            f"Handle operation {handle.operation} does not match requested operation {operation.value}."
        )
        return AWSInfraHandleResponse(
            handle=handle_id,
            message="Handle operation does not match requested operation.",
        )

    current_time = datetime.now(timezone.utc).timestamp()
    if handle.requested_time - current_time > HANDLE_RESPONSE_TIMEOUT:
        return await _build_handle_response_payload(handle_id, handle, timeout=True)

    if handle.response_received != "True":
        return AWSInfraHandleResponse(
            handle=handle_id,
        )

    return await _build_handle_response_payload(handle_id, handle)


async def _build_handle_response_payload(
    handle_id: str, handle: Handle, timeout: bool = False
):
    response_content = (
        json.loads(handle.response_content) if handle.response_content else {}
    )
    payload = {
        "result": not timeout and response_content.get("error", "") == "",
        "handle": handle_id,
    }

    print("Received payload: ", handle.response_content)

    if timeout:
        payload["message"] = "Handle response timed out."
    elif response_content.get("error", "") != "":
        error, message = AWSInfraServiceError.parse(response_content["error"])
        payload["message"] = message
        payload["error"] = error
    if handle.operation == AWSInfraOperationType.CHECK_ROLE:
        payload["session_credentials_retrieved"] = response_content.get(
            "session_credentials_retrieved", False
        )
        return AWSInfraCheckRoleReceivedResponse(**payload)

    canarydrop = queries.get_canarydrop(Canarytoken(value=handle.canarytoken))
    if handle.operation == AWSInfraOperationType.INVENTORY:
        save_current_assets(canarydrop, response_content.get("assets", {}))
        payload["proposed_plan"] = await generate_proposed_plan(canarydrop)
        if is_ingesting(canarydrop):
            filter_decoys_from_inventory(canarydrop)
        return AWSInfraInventoryCustomerAccountReceivedResponse(**payload)

    if handle.operation == AWSInfraOperationType.SETUP_INGESTION:
        payload["terraform_module_snippet"] = get_module_snippet(canarydrop)
        payload["role_cleanup_commands"] = get_role_cleanup_commands(canarydrop)
        return AWSInfraSetupIngestionReceivedResponse(**payload)

    if handle.operation == AWSInfraOperationType.TEARDOWN:
        payload["role_cleanup_commands"] = get_role_cleanup_commands(canarydrop)
        return AWSInfraTeardownReceivedResponse(**payload)

    # this should never happen
    logging.error(f"Unknown operation type {handle.operation} for handle {handle_id}.")


def filter_decoys_from_inventory(canarydrop: Canarydrop):
    """
    Filter out decoy assets from the inventory of the canarydrop.
    """
    inventory = json.loads(canarydrop.aws_inventoried_assets)
    decoys = json.loads(canarydrop.aws_deployed_assets)
    for asset_type in AWSInfraAssetType:
        if asset_type.value in inventory["assets"]:
            inventory["assets"][asset_type.value] = [
                asset
                for asset in inventory["assets"][asset_type.value]
                if asset not in decoys.get(asset_type.value, [])
            ]
    save_current_assets(canarydrop, inventory)


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
    # Clear inventory
    delete_current_assets(canarydrop)
    variables = generate_tf_variables(canarydrop, plan)
    upload_tf_module(
        canarydrop.canarytoken.value(), canarydrop.aws_tf_module_prefix, variables
    )


def get_canarydrop_from_handle(handle_id: str):
    canarydrop = queries.get_canarydrop(
        Canarytoken(
            value=queries.get_aws_management_lambda_handle(handle_id).get("canarytoken")
        )
    )
    return canarydrop


def get_module_snippet(canarydrop: Canarydrop):
    """
    Return the snippet that can be pasted in the customer's terraform.
    """
    return {
        "module": "canarytoken_infra",  # pass this to the frontend for in case we change it
        "source": f"https://{settings.AWS_INFRA_TF_MODULE_BUCKET}.s3.eu-west-1.amazonaws.com/{canarydrop.aws_tf_module_prefix}/{canarydrop.canarytoken.value()}/tf.zip",
    }
