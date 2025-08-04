from unittest.mock import Mock, patch
import pytest

from canarytokens.aws_infra.operations import (
    get_role_create_commands,
    get_role_cleanup_commands,
    start_operation,
    get_module_snippet,
)
from canarytokens.aws_infra.data_generation import (
    generate_names,
    generate_children_names,
    name_generation_limit_usage,
    name_generation_usage_consume,
)

from canarytokens.aws_infra.state_management import (
    update_state,
)
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import (
    AWSInfraAssetType,
    AWSInfraOperationType,
    AWSInfraState,
)
from canarytokens.tokens import Canarytoken
from canarytokens.exceptions import (
    AWSInfraOperationNotAllowed,
)


# Test Fixtures
@pytest.fixture
def mock_canarydrop():
    """Create a mock Canarydrop instance for testing."""
    canarydrop = Mock(spec=Canarydrop)
    canarydrop.canarytoken = Mock(spec=Canarytoken)
    canarydrop.canarytoken.value.return_value = "test_token_123"
    canarydrop.aws_account_id = "123456789012"
    canarydrop.aws_region = "us-east-1"
    canarydrop.aws_customer_iam_access_external_id = "external_id_123"
    canarydrop.aws_infra_inventory_role = "CanarytokensInventoryRole"
    canarydrop.aws_deployed_assets = '{"s3_bucket": ["bucket1", "bucket2"]}'
    canarydrop.aws_saved_plan = '{"s3_bucket": []}'
    canarydrop.aws_tf_module_prefix = "prefix123"
    canarydrop.aws_infra_state = AWSInfraState.INITIAL
    canarydrop.aws_data_generation_requests_made = 0
    canarydrop.aws_infra_ingestion_bus_name = "test-bus"
    return canarydrop


@pytest.fixture
def sample_inventory():
    """Sample AWS inventory for testing."""
    return {
        AWSInfraAssetType.S3_BUCKET: [
            "employee_data_1234",
            "project_files_1234",
            "password_storage_1234",
        ],
        AWSInfraAssetType.SQS_QUEUE: ["PaymentProcessingQueue", "NotificationQueue"],
        AWSInfraAssetType.SSM_PARAMETER: [
            "/app/config/db_password",
            "/app/config/api_key",
        ],
        AWSInfraAssetType.SECRETS_MANAGER_SECRET: ["prod/db/password"],
        AWSInfraAssetType.DYNAMO_DB_TABLE: ["UserSessions", "TransactionHistory"],
    }


class TestOperations:
    def test_get_role_create_commands(self, mock_canarydrop):
        """Test getting role creation commands."""
        result = get_role_create_commands(mock_canarydrop)

        assert result["role_name"] == mock_canarydrop.aws_infra_inventory_role
        assert (
            result["external_id"] == mock_canarydrop.aws_customer_iam_access_external_id
        )
        assert result["customer_aws_account"] == mock_canarydrop.aws_account_id

    def test_get_role_cleanup_commands(self, mock_canarydrop):
        """Test getting role cleanup commands."""
        result = get_role_cleanup_commands(mock_canarydrop)

        assert result["role_name"] == mock_canarydrop.aws_infra_inventory_role
        assert result["customer_aws_account"] == mock_canarydrop.aws_account_id

    @patch("canarytokens.aws_infra.operations.queries")
    @patch("canarytokens.aws_infra.operations.queue_management_request")
    @patch("canarytokens.aws_infra.operations.generate_handle_id")
    @patch("canarytokens.aws_infra.operations.is_ingesting")
    @pytest.mark.parametrize(
        "operation_type",
        [
            AWSInfraOperationType.CHECK_ROLE,
            AWSInfraOperationType.INVENTORY,
            AWSInfraOperationType.SETUP_INGESTION,
            AWSInfraOperationType.TEARDOWN,
        ],
    )
    def test_start_operation(
        self,
        mock_is_ingesting,
        mock_generate_handle_id,
        mock_queue_request,
        mock_queries,
        mock_canarydrop,
        operation_type,
    ):
        """Test starting an operation will queue a request and return a handle."""
        fake_handle_id = "handle123"
        mock_generate_handle_id.return_value = fake_handle_id
        mock_is_ingesting.return_value = False

        result = start_operation(operation_type, mock_canarydrop)

        assert result == fake_handle_id
        mock_queries.add_aws_management_lambda_handle.assert_called_once()
        mock_queue_request.assert_called_once()

    def test_get_module_snippet(self, mock_canarydrop):
        """Test getting Terraform module snippet."""
        with patch("canarytokens.aws_infra.operations.settings") as mock_settings:
            mock_settings.AWS_INFRA_TF_MODULE_BUCKET = "test-bucket"

            result = get_module_snippet(mock_canarydrop)

            expected_source = f"https://test-bucket.s3.eu-west-1.amazonaws.com/{mock_canarydrop.aws_tf_module_prefix}/{mock_canarydrop.canarytoken.value()}/tf.zip"
            assert result["module"] == "canarytoken_infra"
            assert result["source"] == expected_source


# Test Data Generation Functions
class TestDataGeneration:
    """Test cases for data generation functions."""

    @pytest.mark.skip("Skipping this to avoid incurring costs")
    @pytest.mark.parametrize(
        "asset_type", [asset_type for asset_type in AWSInfraAssetType]
    )
    @pytest.mark.asyncio
    async def test_generate_names(self, asset_type):
        """Test generating asset names."""

        result = await generate_names(asset_type, ["nameforasset"], 10)

        assert result.asset_type == asset_type
        assert len(result.suggested_names) == 10

    @pytest.mark.skip("Skipping this to avoid incurring costs")
    @pytest.mark.parametrize(
        "parent_asset_type", [asset_type for asset_type in AWSInfraAssetType]
    )
    @pytest.mark.asyncio
    async def test_generate_children_names(self, parent_asset_type):
        """Test generating child asset names."""

        if parent_asset_type not in [
            AWSInfraAssetType.S3_BUCKET,
            AWSInfraAssetType.DYNAMO_DB_TABLE,
        ]:
            with pytest.raises(ValueError):
                await generate_children_names(parent_asset_type, "parentname", 10)
        else:
            result = await generate_children_names(parent_asset_type, "parentname", 10)
            assert len(result) == 10

    @patch("canarytokens.aws_infra.data_generation.save_canarydrop")
    def test_name_generation_usage(self, mock_save, mock_canarydrop):
        """Test consuming name generation usage."""
        mock_canarydrop.aws_data_generation_requests_made = 5

        with patch("canarytokens.aws_infra.data_generation.settings") as mock_settings:
            mock_settings.AWS_INFRA_NAME_GENERATION_LIMIT = 50

            name_generation_usage_consume(mock_canarydrop, 2)

            assert mock_canarydrop.aws_data_generation_requests_made == 7
            mock_save.assert_called_once()

            usage = name_generation_limit_usage(mock_canarydrop)

            assert usage.count == 7
            assert usage.remaining == 43

    def test_name_generation_usage_consume_exceeds_limit(self, mock_canarydrop):
        """Test consuming usage when exceeding limit."""
        mock_canarydrop.aws_data_generation_requests_made = 50

        with patch("canarytokens.aws_infra.data_generation.settings") as mock_settings:
            mock_settings.AWS_INFRA_NAME_GENERATION_LIMIT = 50

            name_generation_usage_consume(mock_canarydrop, 10)
            usage = name_generation_limit_usage(mock_canarydrop)
            assert mock_canarydrop.aws_data_generation_requests_made == 50
            assert usage.count == 50
            assert usage.remaining == 0


# Test State Management Functions
class TestStateManagement:
    """Test cases for state management functions."""

    @pytest.mark.parametrize(
        "current_state, next_state, expected_result",
        [
            (AWSInfraState.INITIAL, AWSInfraState.CHECK_ROLE, True),
            (AWSInfraState.CHECK_ROLE, AWSInfraState.INVENTORY, False),
            (
                AWSInfraState.CHECK_ROLE | AWSInfraState.SUCCEEDED,
                AWSInfraState.SETUP_INGESTION,
                True,
            ),
            (AWSInfraState.INVENTORY, AWSInfraState.SETUP_INGESTION, False),
            (
                AWSInfraState.INVENTORY | AWSInfraState.SUCCEEDED,
                AWSInfraState.SETUP_INGESTION,
                False,
            ),
            (
                AWSInfraState.INVENTORY | AWSInfraState.SUCCEEDED,
                AWSInfraState.GENERATE_CHILD_ASSETS,
                True,
            ),
            (
                AWSInfraState.GENERATE_CHILD_ASSETS | AWSInfraState.SUCCEEDED,
                AWSInfraState.PLAN,
                True,
            ),
            (
                AWSInfraState.PLAN | AWSInfraState.SUCCEEDED,
                AWSInfraState.SETUP_INGESTION,
                True,
            ),
            (
                AWSInfraState.SETUP_INGESTION | AWSInfraState.SUCCEEDED,
                AWSInfraState.CHECK_ROLE,
                False,
            ),
        ],
    )
    @patch("canarytokens.aws_infra.state_management.queries")
    def test_update_state(
        self, mock_queries, mock_canarydrop, current_state, next_state, expected_result
    ):
        """Test updating state with valid transition."""
        mock_canarydrop.aws_infra_state = current_state

        if expected_result:
            update_state(mock_canarydrop, next_state)

            assert mock_canarydrop.aws_infra_state == next_state
            mock_queries.save_canarydrop.assert_called_once()
        else:
            with pytest.raises(AWSInfraOperationNotAllowed):
                update_state(mock_canarydrop, next_state)
