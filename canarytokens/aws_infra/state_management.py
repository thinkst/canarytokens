from canarytokens import queries
from canarytokens.aws_infra.operations import delete_external_id, generate_external_id
from canarytokens.canarydrop import Canarydrop
from canarytokens.exceptions import OperationNotAllowed
from canarytokens.models import AWSInfraState
from canarytokens.settings import FrontendSettings

settings = FrontendSettings()


def allow_next_state(canarydrop: Canarydrop, next_state: AWSInfraState) -> bool:
    """
    Check if the next state is allowed based on the current state of the canarydrop.
    """
    if settings.DEV:  # temporary override for development purposes
        return settings.DEV
    if canarydrop.aws_infra_state == AWSInfraState.INITIAL:
        return next_state == AWSInfraState.ROLE_CHECKING

    elif (
        canarydrop.aws_infra_state in AWSInfraState.ROLE_CHECKING
        and canarydrop.aws_customer_iam_access_external_id is not None
    ):
        return next_state in AWSInfraState.INVENTORYING

    elif canarydrop.aws_infra_state in AWSInfraState.INVENTORYING:
        return next_state in AWSInfraState.PLANNING

    elif canarydrop.aws_infra_state in AWSInfraState.PLANNING:
        return next_state in AWSInfraState.INGESTING

    elif (
        canarydrop.aws_infra_state in AWSInfraState.INGESTING
        and canarydrop.aws_customer_iam_access_external_id is not None
    ):
        return next_state in AWSInfraState.INVENTORYING

    return False


def update_state(canarydrop: Canarydrop, new_state: AWSInfraState):
    """
    Update the state of the canarydrop to the new state.
    """
    if not allow_next_state(canarydrop, new_state):
        raise OperationNotAllowed("Operation not allowed at this stage.")

    if canarydrop.aws_infra_state == AWSInfraState.INITIAL:
        canarydrop.aws_customer_iam_access_external_id = generate_external_id()

    if canarydrop.aws_infra_state == AWSInfraState.PLANNING:
        delete_external_id(canarydrop)

    if canarydrop.aws_infra_state == AWSInfraState.INGESTING:
        canarydrop.aws_infra_state = new_state | AWSInfraState.EDITING
    else:
        canarydrop.aws_infra_state = new_state
    queries.save_canarydrop(canarydrop)
