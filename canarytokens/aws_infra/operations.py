import json
import logging

from datetime import datetime, timezone
from pydantic import BaseModel

from canarytokens import queries
from canarytokens.aws_infra.aws_management import (
    queue_management_request,
    upload_tf_module,
)
from canarytokens.aws_infra.data_generation import name_generation_limit_usage
from canarytokens.aws_infra.plan_generation import (
    generate_proposed_plan,
    save_plan,
)
from canarytokens.aws_infra.state_management import is_ingesting, set_ingestion_bus
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

from canarytokens.aws_infra.db_queries import (
    delete_current_assets,
    get_current_assets,
    save_current_assets,
)

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


def start_operation(
    operation: AWSInfraOperationType, canarydrop: Canarydrop, handle_id=None
):
    "Create a new handle entry in the redis DB and trigger the specified operation"
    initial_response_received_status = (
        is_ingesting(canarydrop) and operation == AWSInfraOperationType.SETUP_INGESTION
    )
    if handle_id is None:
        handle_id = generate_handle_id()
        handle = Handle(
            canarytoken=canarydrop.canarytoken.value(),
            operation=operation.value,
            requested_time=datetime.now(timezone.utc).timestamp(),
            response_received=str(initial_response_received_status),
            response_content="",
        )
        queries.add_aws_management_lambda_handle(
            handle_id,
            handle.dict(),
        )
    else:
        # reset existing handle to allow setup-ingestion retry after ingestion bus provisioning
        queries.reset_aws_management_lambda_handle_received(handle_id, operation.value)

    if initial_response_received_status is False:
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
            "plan_mode": "create" if not is_ingesting(canarydrop) else "edit",
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


def _get_error_message(
    error: AWSInfraServiceError, canarydrop: Canarydrop = None
) -> str:

    role = f" ({canarydrop.aws_infra_inventory_role})" if canarydrop else ""
    account = f" ({canarydrop.aws_account_id})" if canarydrop else ""
    region = f" ({canarydrop.aws_region})" if canarydrop else ""

    """
    Return the error message associated with the given AWSInfraServiceError.
    """
    SERVICE_ERROR_MESSAGE_MAP = {
        AWSInfraServiceError.FAILURE_CHECK_ROLE: f"Could not assume the role{role} in the account. Please make sure the role exists and that the external ID is correct.",
        AWSInfraServiceError.FAILURE_INVENTORY_REGION_DISABLED: f"The region{region} is not enabled in the AWS account{account}. Please enable it and try again or choose a different region.",
        AWSInfraServiceError.FAILURE_INGESTION_SETUP: f'Could not setup alerting. If you have previously created an AWS Infra Canarytoken in this AWS account{account} in the same region{region}, then you need to delete the existing Canarytoken before creating a new one. Alternatively, you can rather edit the decoys in the existing Canarytoken. Hint: if you\'ve lost your Manage link, you can retrieve it by clicking on "My Canarytokens" at the top of the page.',
        AWSInfraServiceError.FAILURE_INGESTION_TEARDOWN: "",  # UI does not show this error
        AWSInfraServiceError.FAILURE_INVENTORY_ACCESS_DENIED: f"Could not retrieve the inventory of the AWS account{account} because access was denied. Please make sure the policy, Canarytokens-Inventory-ReadOnly-Policy, is attached to the inventory role{role} that you created for us to inventory your resources.",
        AWSInfraServiceError.FAILURE_INVENTORY_REGION_DISABLED: f"The region{region} is not enabled in the AWS account{account}. Please enable it and try again or choose a different region.",
        AWSInfraServiceError.FAILURE_INVENTORY_TOKEN_EXISTS: f"There's already a Canarytoken setup in{region} for {account}, so you won't be able to continue. Either edit or delete that Canarytoken through it's Manage link. If you do delete the Canarytoken, we recommend first running `$ terraform destroy` on the decoy Terraform plan, to remove the decoys from your AWS account before the Canarytoken is removed.",
        AWSInfraServiceError.FAILURE_INGESTION_BUS_PROVISION: "Something went wrong while trying to setup alerting. Please try again later.",
        AWSInfraServiceError.NO_ERROR: "",
        AWSInfraServiceError.REQ_HANDLE_INVALID: "The handle ID provided is invalid.",
        AWSInfraServiceError.REQ_HANDLE_TIMEOUT: "Handle response timed out.",
        AWSInfraServiceError.UNHANDLED_ERROR: "Something went wrong while processing the request. Please try again later.",
    }

    return SERVICE_ERROR_MESSAGE_MAP.get(error, "An unknown error occurred.")


def _allowed_handle_operation(handle: Handle, operation: AWSInfraOperationType):
    if handle.operation == AWSInfraOperationType.PROVISION_INGESTION_BUS:
        # the UI doesn't know about provisioning ingestion buses, so allow both operations
        return operation in [
            AWSInfraOperationType.PROVISION_INGESTION_BUS,
            AWSInfraOperationType.SETUP_INGESTION,
        ]
    return handle.operation == operation.value


async def get_handle_response(handle_id: str, operation: AWSInfraOperationType):
    """
    Check if a response has been added to the specified handle in the redis DB and return it.
    """
    handle = queries.get_aws_management_lambda_handle(handle_id)
    default_error = AWSInfraServiceError.REQ_HANDLE_INVALID
    default_error_message = _get_error_message(default_error)

    if not handle:
        return AWSInfraHandleResponse(
            handle=handle_id,
            error=default_error.value,
            message=default_error_message,
        )

    handle = Handle(**handle)
    if not _allowed_handle_operation(handle, operation):
        return AWSInfraHandleResponse(
            handle=handle_id,
            message=default_error_message,
            error=default_error.value,
        )

    if handle.response_received != "True":
        return AWSInfraHandleResponse(
            handle=handle_id,
        )

    current_time = datetime.now(timezone.utc).timestamp()
    return await _build_handle_response_payload(
        handle_id,
        handle,
        timeout=current_time - handle.requested_time > HANDLE_RESPONSE_TIMEOUT,
    )


async def _handle_provision_ingestion_bus(
    payload: dict, response_content: dict, canarydrop: Canarydrop
):
    if payload["result"]:
        bus_name = response_content.get("bus_name")
        print(f"Provisioned new ingestion bus: {bus_name}")
        set_ingestion_bus(canarydrop, bus_name)
        if canarydrop.aws_saved_plan:
            # reupload the tf module with the new bus name
            upload_tf_module(canarydrop, json.loads(canarydrop.aws_saved_plan))
        # restart the original operation that needed a new ingestion bus
        start_operation(
            AWSInfraOperationType.SETUP_INGESTION, canarydrop, payload["handle"]
        )
    return AWSInfraHandleResponse(**payload)


async def _handle_check_role(
    payload: dict, response_content: dict, canarydrop: Canarydrop
):
    payload["session_credentials_retrieved"] = response_content.get(
        "session_credentials_retrieved", False
    )
    return AWSInfraCheckRoleReceivedResponse(**payload)


async def _handle_inventory(
    payload: dict, response_content: dict, canarydrop: Canarydrop
):
    if not payload["result"]:
        return AWSInfraInventoryCustomerAccountReceivedResponse(**payload)

    save_current_assets(canarydrop, response_content.get("assets", {}))
    payload.update(
        {
            "proposed_plan": {"assets": await generate_proposed_plan(canarydrop)},
            "data_generation_remaining": name_generation_limit_usage(
                canarydrop
            ).remaining,
        }
    )
    # remove decoys from inventory so that they don't influence calls to generate-data-choices
    if is_ingesting(canarydrop):
        filter_decoys_from_inventory(canarydrop)
    return AWSInfraInventoryCustomerAccountReceivedResponse(**payload)


async def _handle_setup_ingestion(
    payload: dict, response_content: dict, canarydrop: Canarydrop
):
    payload["role_cleanup_commands"] = get_role_cleanup_commands(canarydrop)
    if payload["result"]:
        payload["terraform_module_snippet"] = get_module_snippet(canarydrop)
    return AWSInfraSetupIngestionReceivedResponse(**payload)


async def _handle_teardown(
    payload: dict, response_content: dict, canarydrop: Canarydrop
):
    payload["role_cleanup_commands"] = get_role_cleanup_commands(canarydrop)
    return AWSInfraTeardownReceivedResponse(**payload)


async def _build_handle_response_payload(
    handle_id: str, handle: Handle, timeout: bool = False
):
    response_content = (
        json.loads(handle.response_content) if handle.response_content else {}
    )
    error = (
        AWSInfraServiceError.parse(response_content.get("error", ""))
        if not timeout
        else AWSInfraServiceError.REQ_HANDLE_TIMEOUT
    )
    canarydrop = queries.get_canarydrop(Canarytoken(value=handle.canarytoken))

    if error == AWSInfraServiceError.FAILURE_INGESTION_BUS_IS_FULL:
        logging.info("Provisioning new ingestion bus...")
        start_operation(
            AWSInfraOperationType.PROVISION_INGESTION_BUS, canarydrop, handle_id
        )
        return AWSInfraHandleResponse(handle=handle_id)

    payload = {
        "result": error == AWSInfraServiceError.NO_ERROR,
        "handle": handle_id,
        "message": _get_error_message(error, canarydrop),
        "error": error.value,
    }

    operation = AWSInfraOperationType(handle.operation)

    operation_handlers = {
        AWSInfraOperationType.PROVISION_INGESTION_BUS: _handle_provision_ingestion_bus,
        AWSInfraOperationType.CHECK_ROLE: _handle_check_role,
        AWSInfraOperationType.INVENTORY: _handle_inventory,
        AWSInfraOperationType.SETUP_INGESTION: _handle_setup_ingestion,
        AWSInfraOperationType.TEARDOWN: _handle_teardown,
    }

    handler = operation_handlers.get(operation)
    if handler:
        return await handler(payload, response_content, canarydrop)

    # Fallback for unknown operations, this should never happen
    logging.error(f"Unknown operation type {operation} for handle {handle_id}.")


def filter_decoys_from_inventory(canarydrop: Canarydrop):
    """
    Filter out decoy assets from the inventory of the canarydrop.
    """
    inventory = get_current_assets(canarydrop)
    decoys = json.loads(canarydrop.aws_deployed_assets)
    for asset_type in AWSInfraAssetType:
        if asset_type.value in inventory:
            inventory[asset_type.value] = [
                asset
                for asset in inventory[asset_type.value]
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


async def setup_new_plan(canarydrop: Canarydrop, plan: str):
    """
    Save an AWS Infra plan and upload it to the tf modules S3 bucket.
    """
    await save_plan(canarydrop, plan)
    queries.save_canarydrop(canarydrop)
    # Clear inventory
    delete_current_assets(canarydrop)
    upload_tf_module(canarydrop, plan)


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
