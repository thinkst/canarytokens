import sys
from unittest.mock import Mock, patch
import pytest
from exceptiongroup import ExceptionGroup

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

from canarytokens.aws_infra.plan_generation import (
    AWSInfraAsset,
    AWSInfraPlan,
    _get_event_pattern_length,
    add_new_assets_to_plan,
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
    canarydrop.aws_deployed_assets = '{"S3Bucket": ["bucket1", "bucket2"]}'
    canarydrop.aws_tf_module_prefix = "prefix123"
    canarydrop.aws_infra_state = AWSInfraState.INITIAL
    canarydrop.aws_infra_ingestion_bus_name = "test-bus"
    return canarydrop


MOCK_INVENTORY_DATA = {
    AWSInfraAssetType.S3_BUCKET: [
        "employee-data-1234",
        "project-files-1234",
        "password-storage-1234",
    ],
    AWSInfraAssetType.SQS_QUEUE: ["PaymentProcessingQueue", "NotificationQueue"],
    AWSInfraAssetType.SSM_PARAMETER: [
        "db_password",
        "api_key",
    ],
    AWSInfraAssetType.SECRETS_MANAGER_SECRET: ["password"],
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
        """
        Test the generate_names function to ensure it returns the correct asset type and the expected number of unique suggested names.
        """

        count = 10
        result = await generate_names(asset_type, ["fakename"], count)

        assert result.asset_type == asset_type
        assert len(set(result.suggested_names)) == count

    @pytest.mark.skip("Skipping this to avoid incurring costs")
    @pytest.mark.parametrize(
        "parent_asset_type", [asset_type for asset_type in AWSInfraAssetType]
    )
    @pytest.mark.asyncio
    async def test_generate_children_names(self, parent_asset_type):
        """Test generate_children_names function to ensure it returns the correct number of unique names."""
        count = 10
        if parent_asset_type not in [
            AWSInfraAssetType.S3_BUCKET,
            AWSInfraAssetType.DYNAMO_DB_TABLE,
        ]:
            with pytest.raises(ValueError):
                await generate_children_names(parent_asset_type, "parentname", count)
        else:
            result = await generate_children_names(
                parent_asset_type, "parentname", count
            )
            assert len(set(result)) == count

    def test_name_generation_usage(self, mock_canarydrop, setup_db):
        """Test consuming name generation usage."""
        LIMIT = 50
        CONSUME_COUNT = 2
        with patch("canarytokens.aws_infra.data_generation.settings") as mock_settings:
            mock_settings.AWS_INFRA_NAME_GENERATION_LIMIT = LIMIT
            initial_count = name_generation_limit_usage(mock_canarydrop).count
            assert initial_count == 0

            name_generation_usage_consume(mock_canarydrop, CONSUME_COUNT)
            usage = name_generation_limit_usage(mock_canarydrop)

            assert usage.count == initial_count + CONSUME_COUNT
            assert usage.remaining == LIMIT - CONSUME_COUNT

    def test_name_generation_usage_consume_exceeds_limit(
        self, mock_canarydrop, setup_db
    ):
        """Test consuming usage when exceeding limit."""
        LIMIT = 10
        with patch("canarytokens.aws_infra.data_generation.settings") as mock_settings:
            mock_settings.AWS_INFRA_NAME_GENERATION_LIMIT = LIMIT

            name_generation_usage_consume(mock_canarydrop, LIMIT)
            usage = name_generation_limit_usage(mock_canarydrop)
            assert usage.count == LIMIT
            assert usage.remaining == 0

            name_generation_usage_consume(mock_canarydrop, 1)
            usage = name_generation_limit_usage(mock_canarydrop)
            assert usage.count == LIMIT
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
                False,
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
                True,
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


VALID_PLAN = {
    "S3Bucket": [
        {
            "bucket_name": "test-bucket-123",
            "objects": ["file1.txt", "file2.pdf"],
            "off_inventory": False,
        }
    ],
    "SQSQueue": [{"sqs_queue_name": "test-queue-456", "off_inventory": False}],
    "SSMParameter": [{"ssm_parameter_name": "test-param", "off_inventory": False}],
    "SecretsManagerSecret": [{"secret_name": "test-secret", "off_inventory": False}],
    "DynamoDBTable": [
        {
            "table_name": "TestTable",
            "table_items": ["item1", "item2"],
            "off_inventory": False,
        }
    ],
}


class TestPlanGenerationValidation:
    """Test cases for AWS Infrastructure Plan validation."""

    @pytest.mark.parametrize(
        "asset",
        [
            {"bucket_name": "Bucket-name-123"},
            {"bucket_name": "xn--invalid-bucket"},
            {"sqs_queue_name": "invalid-queue.name"},
            {"ssm_parameter_name": "aws-invalid-param"},
            {"ssm_parameter_name": "/invalid/param"},
            {"secret_name": "invalid..secret"},
            {"table_name": "ab"},
        ],
    )
    def test_asset_name_invalid(self, asset):
        """Test invalid asset name."""
        with pytest.raises(ValueError):
            AWSInfraAsset(**asset)

    def test_aws_infra_plan_valid_creation(self):
        """Test creating a valid AWS infrastructure plan."""
        plan = AWSInfraPlan.parse_obj(VALID_PLAN)
        assert plan.validation_errors is None

    @patch("canarytokens.aws_infra.plan_generation.get_current_assets")
    def test_aws_infra_plan_with_canarydrop_context(
        self, mock_get_assets, mock_canarydrop
    ):
        """Test plan validation with canarydrop context."""

        mock_get_assets.return_value = MOCK_INVENTORY_DATA

        plan_data = {
            "S3Bucket": [
                {
                    "bucket_name": MOCK_INVENTORY_DATA["S3Bucket"][0],
                    "off_inventory": False,
                }  # Exists in inventory
            ]
        }

        plan = AWSInfraPlan.from_dict_with_canarydrop(plan_data, mock_canarydrop)
        assert plan.validation_errors is not None
        assert "already exists in AWS account" in plan.validation_errors[0]

    def test_event_pattern_length_calculation(self):
        """Test event pattern length calculation function."""

        length = _get_event_pattern_length(VALID_PLAN, "us-east-1")
        assert length == 567

    @patch("canarytokens.aws_infra.plan_generation._add_assets_for_type")
    @pytest.mark.asyncio
    async def test_add_new_assets_to_plan_exception_group(self, mock_add_assets):
        """Test ExceptionGroup handling in add_new_assets_to_plan."""

        mock_error = RuntimeError("Mock error")

        if sys.version_info < (3, 11):
            exception_group = ExceptionGroup("Multiple errors occurred", [mock_error])
            mock_add_assets.side_effect = exception_group
        else:
            mock_add_assets.side_effect = mock_error

        aws_deployed_assets = {}
        aws_inventoried_assets = {}
        plan = {asset_type.value: [] for asset_type in AWSInfraAssetType}

        # Should catch ExceptionGroup and raise RuntimeError
        with pytest.raises(
            RuntimeError,
            match=r"Exception\(s\) occurred when trying to add new assets to the decoy plan",
        ):
            await add_new_assets_to_plan(
                aws_deployed_assets, aws_inventoried_assets, plan
            )
