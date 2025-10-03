import logging

from canarytokens import queries
from canarytokens.aws_infra.aws_management import get_current_ingestion_bus
from canarytokens.aws_infra.utils import (
    AWS_INFRA_ENABLED,
    generate_external_id,
    generate_inventory_role_name,
    generate_tf_module_prefix,
)
from canarytokens.canarydrop import Canarydrop
from canarytokens.exceptions import (
    AWSInfraOperationNotAllowed,
    CanarytokenTypeNotEnabled,
)
from canarytokens.models import AWSInfraState
from canarytokens.settings import FrontendSettings

settings = FrontendSettings()
OVERLAY_STATES = AWSInfraState.INGESTING


def initialise(canarydrop: Canarydrop) -> bool:
    """
    Initialize the AWS infrastructure state for the canarydrop.
    This sets the initial state and generates an external ID if not already set.
    """

    if not AWS_INFRA_ENABLED:
        logging.error(
            "The required settings have not been configured on the server for the AWS Infra Canarytoken."
        )
        raise CanarytokenTypeNotEnabled(
            "The required settings have not been set for the AWS Infra Canarytoken in frontend.env. See settings.py for required settings."
        )
    canarydrop.aws_tf_module_prefix = generate_tf_module_prefix()
    canarydrop.aws_infra_ingestion_bus_name = get_current_ingestion_bus()
    canarydrop.aws_customer_iam_access_external_id = generate_external_id()
    canarydrop.aws_infra_inventory_role = generate_inventory_role_name()
    canarydrop.aws_infra_state = AWSInfraState.INITIAL


def allow_next_state(canarydrop: Canarydrop, next_state: AWSInfraState = None) -> bool:
    """
    Check if the next state is allowed based on the current state of the canarydrop. If the next state is None,
    it checks if the canarydrop has been initialised, i.e. has any state set.
    """
    state_transition_allow_map = {
        AWSInfraState.INITIAL: [AWSInfraState.CHECK_ROLE],
        AWSInfraState.CHECK_ROLE: [AWSInfraState.CHECK_ROLE],
        AWSInfraState.CHECK_ROLE
        | AWSInfraState.SUCCEEDED: [AWSInfraState.CHECK_ROLE, AWSInfraState.INVENTORY],
        AWSInfraState.INVENTORY: [AWSInfraState.INVENTORY, AWSInfraState.CHECK_ROLE],
        AWSInfraState.INVENTORY
        | AWSInfraState.SUCCEEDED: [
            AWSInfraState.INVENTORY,
            AWSInfraState.CHECK_ROLE,
            AWSInfraState.GENERATE_CHILD_ASSETS,
            AWSInfraState.PLAN,
        ],
        AWSInfraState.GENERATE_CHILD_ASSETS: [
            AWSInfraState.INVENTORY,
            AWSInfraState.GENERATE_CHILD_ASSETS,
            AWSInfraState.CHECK_ROLE,
            AWSInfraState.PLAN,
        ],
        AWSInfraState.GENERATE_CHILD_ASSETS
        | AWSInfraState.SUCCEEDED: [
            AWSInfraState.INVENTORY,
            AWSInfraState.GENERATE_CHILD_ASSETS,
            AWSInfraState.PLAN,
            AWSInfraState.CHECK_ROLE,
        ],
        AWSInfraState.PLAN: [AWSInfraState.PLAN, AWSInfraState.CHECK_ROLE],
        AWSInfraState.PLAN
        | AWSInfraState.SUCCEEDED: [
            AWSInfraState.SETUP_INGESTION,
            AWSInfraState.PLAN,
            AWSInfraState.CHECK_ROLE,
        ],
        AWSInfraState.SETUP_INGESTION: [
            AWSInfraState.SETUP_INGESTION,
            AWSInfraState.CHECK_ROLE,
            AWSInfraState.PLAN,
        ],  # if setup-ingestion fails, we can retry from check-role
        AWSInfraState.SETUP_INGESTION
        | AWSInfraState.SUCCEEDED: [
            AWSInfraState.SETUP_INGESTION,
            AWSInfraState.CHECK_ROLE,
            AWSInfraState.PLAN,
        ],
    }
    return next_state in state_transition_allow_map.get(
        get_base_state(canarydrop.aws_infra_state), []
    )


def update_state(canarydrop: Canarydrop, new_state: AWSInfraState, **kwargs) -> None:
    """
    Update the state of the canarydrop to the new state.
    """
    if not allow_next_state(canarydrop, new_state):
        logging.error(
            f"Cannot update state from {canarydrop.aws_infra_state} to {new_state}."
        )
        raise AWSInfraOperationNotAllowed(
            "This operation is not allowed for the current Canarytoken state."
        )

    if new_state == AWSInfraState.CHECK_ROLE:

        new_external_id = kwargs.get("external_id")
        canarydrop.aws_customer_iam_access_external_id = (
            new_external_id or canarydrop.aws_customer_iam_access_external_id
        )
        if not canarydrop.aws_customer_iam_access_external_id:
            logging.error("Trying to set the CHECK_ROLE state without an external ID.")
            raise AWSInfraOperationNotAllowed("Please provide an external ID.")

    canarydrop.aws_infra_state = (
        get_overlay_state(canarydrop.aws_infra_state) | new_state
    )
    queries.save_canarydrop(canarydrop)


def get_base_state(state: AWSInfraState) -> AWSInfraState:
    """
    Return the base state of the given state.
    """
    return state & ~OVERLAY_STATES


def get_overlay_state(state: AWSInfraState) -> AWSInfraState:
    """
    Return the overlay state of the given state.
    """
    return state & OVERLAY_STATES


def in_state(canarydrop: Canarydrop, state: AWSInfraState) -> bool:
    """
    Check if the canarydrop is in the specified state.
    """
    return (canarydrop.aws_infra_state & state) == state


def mark_succeeded(canarydrop: Canarydrop):
    """
    Mark the state as succeeded by adding the overlay states.
    """
    canarydrop.aws_infra_state = canarydrop.aws_infra_state | AWSInfraState.SUCCEEDED


def mark_failed(canarydrop: Canarydrop):
    """
    Mark the state as failed by removing the SUCCEEDED overlay state.
    """
    canarydrop.aws_infra_state = canarydrop.aws_infra_state & ~AWSInfraState.SUCCEEDED


def mark_ingesting(canarydrop: Canarydrop):
    """
    Mark the state as ingesting by adding the INGESTING overlay state.
    """
    canarydrop.aws_customer_iam_access_external_id = ""
    canarydrop.aws_infra_state = canarydrop.aws_infra_state | AWSInfraState.INGESTING


def is_succeeded(canarydrop: Canarydrop) -> bool:
    """
    Check if the canarydrop's state is currently succeeded.
    """
    return (
        canarydrop.aws_infra_state & AWSInfraState.SUCCEEDED
    ) == AWSInfraState.SUCCEEDED


def is_ingesting(canarydrop: Canarydrop) -> bool:
    """
    Check if the canarydrop's state is currently ingesting.
    """
    return (
        canarydrop.aws_infra_state & AWSInfraState.INGESTING
    ) == AWSInfraState.INGESTING


def is_initialised(canarydrop: Canarydrop) -> bool:
    """
    Check if the canarydrop has been initialised, i.e. has any state set.
    """
    return canarydrop.aws_infra_state is not None


def set_ingestion_bus(canarydrop: Canarydrop, bus_name: str) -> None:
    """
    Set the ingestion bus name for the canarydrop.
    """
    if is_ingesting(canarydrop):
        error_message = (
            "Cannot set ingestion bus after canarydrop has started ingesting."
        )
        logging.error(error_message)
        raise RuntimeError(error_message)
    canarydrop.aws_infra_ingestion_bus_name = bus_name
    queries.save_canarydrop(canarydrop)
