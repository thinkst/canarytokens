# Integration Tests


from unittest.mock import patch

from canarytokens.aws_infra.operations import setup_new_plan
from canarytokens.aws_infra.state_management import (
    get_base_state,
    initialise,
    is_succeeded,
    mark_succeeded,
    update_state,
)
from canarytokens.models import AWSInfraState


@patch("canarytokens.aws_infra.operations.save_plan")
@patch("canarytokens.aws_infra.operations.upload_tf_module")
@patch("canarytokens.aws_infra.operations.generate_tf_variables")
@patch("canarytokens.aws_infra.operations.delete_current_assets")
@patch("canarytokens.aws_infra.operations.queries")
def test_setup_new_plan_integration(
    mock_queries,
    mock_delete_assets,
    mock_gen_variables,
    mock_upload,
    mock_save_plan,
    mock_canarydrop,
):
    """Test complete setup of new plan integration."""
    plan = {"s3_bucket": [{"bucket_name": "test-bucket"}]}
    mock_gen_variables.return_value = {"test": "value"}

    setup_new_plan(mock_canarydrop, plan)

    mock_save_plan.assert_called_once_with(mock_canarydrop, plan)
    mock_queries.save_canarydrop.assert_called_once()
    mock_delete_assets.assert_called_once()
    mock_upload.assert_called_once()


@patch("canarytokens.aws_infra.state_management.queries")
def test_state_transition_workflow(self, mock_queries, mock_canarydrop):
    """Test a complete state transition workflow."""
    # Initialize
    mock_canarydrop.aws_infra_state = None
    initialise(mock_canarydrop)
    assert mock_canarydrop.aws_infra_state == AWSInfraState.INITIAL

    # Transition to CHECK_ROLE
    update_state(mock_canarydrop, AWSInfraState.CHECK_ROLE)
    assert get_base_state(mock_canarydrop.aws_infra_state) == AWSInfraState.CHECK_ROLE

    # Mark as succeeded
    mark_succeeded(mock_canarydrop)
    assert is_succeeded(mock_canarydrop) is True

    # Transition to INVENTORY
    update_state(mock_canarydrop, AWSInfraState.INVENTORY)
    assert get_base_state(mock_canarydrop.aws_infra_state) == AWSInfraState.INVENTORY
