from typing import Any, List, Literal, Optional, Union
from .common import (
    BaseModel,
    TokenEditRequest,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
    enum,
    json_safe_dict,
)


class AWSInfraAssetType(enum.StrEnum):
    S3_BUCKET = "S3Bucket"
    SQS_QUEUE = "SQSQueue"
    SSM_PARAMETER = "SSMParameter"
    SECRETS_MANAGER_SECRET = "SecretsManagerSecret"
    DYNAMO_DB_TABLE = "DynamoDBTable"


class AWSInfraAssetField(enum.StrEnum):
    BUCKET_NAME = "bucket_name"
    OBJECTS = "objects"
    SQS_QUEUE_NAME = "sqs_queue_name"
    SSM_PARAMETER_NAME = "ssm_parameter_name"
    SECRET_NAME = "secret_name"
    TABLE_NAME = "table_name"
    TABLE_ITEMS = "table_items"


class AWSInfraOperationType(enum.StrEnum):
    CHECK_ROLE = "Check-Role"
    INVENTORY = "Inventory"
    SETUP_INGESTION = "Setup-Ingestion"
    PROVISION_INGESTION_BUS = "Provision-Ingestion-Bus"
    TEARDOWN = "Teardown"


class AWSInfraState(enum.Flag):
    INITIAL = enum.auto()
    CHECK_ROLE = enum.auto()
    INVENTORY = enum.auto()
    GENERATE_CHILD_ASSETS = enum.auto()
    PLAN = enum.auto()
    SETUP_INGESTION = enum.auto()
    INGESTING = enum.auto()
    SUCCEEDED = enum.auto()


class AWSInfraServiceError(enum.StrEnum):
    FAILURE_CHECK_ROLE = "FAILURE_CHECK_ROLE"
    FAILURE_INGESTION_BUS_IS_FULL = "FAILURE_INGESTION_BUS_IS_FULL"
    FAILURE_INGESTION_BUS_PROVISION = "FAILURE_INGESTION_BUS_PROVISION"
    FAILURE_INGESTION_SETUP = "FAILURE_INGESTION_SETUP"
    FAILURE_INGESTION_TEARDOWN = "FAILURE_INGESTION_TEARDOWN"
    FAILURE_INVENTORY = "FAILURE_INVENTORY"
    FAILURE_MGMT_RESPONSE = "FAILURE_MGMT_RESPONSE"
    FAILURE_TRIG_ALERT = "FAILURE_TRIG_ALERT"
    FAILURE_INVENTORY_REGION_DISABLED = "FAILURE_INVENTORY_REGION_DISABLED"
    FAILURE_INVENTORY_ACCESS_DENIED = "FAILURE_INVENTORY_ACCESS_DENIED"
    FAILURE_INVENTORY_TOKEN_EXISTS = "FAILURE_INVENTORY_TOKEN_EXISTS"
    OP_MISSING_KEY = "OP_MISSING_KEY"
    REQ_HANDLE_INVALID = "REQ_HANDLE_INVALID"
    REQ_HANDLE_TIMEOUT = "REQ_HANDLE_TIMEOUT"
    REQ_OPERATION_INVALID = "REQ_OPERATION_INVALID"
    REQ_PAYLOAD_INVALID_JSON = "REQ_PAYLOAD_INVALID_JSON"
    REQ_PAYLOAD_UNSUPPORTED = "REQ_PAYLOAD_UNSUPPORTED"
    UNHANDLED_ERROR = "UNHANDLED_ERROR"
    UNKNOWN = "UNKNOWN"
    NO_ERROR = ""

    @classmethod
    def parse(cls, error: Optional[str] = None):
        if not error:
            return cls.NO_ERROR

        try:
            code = error.split("::")[0]
            return cls(code)
        except ValueError:
            return cls.UNKNOWN


class AWSInfraConfigStartRequest(BaseModel):
    canarytoken: str
    auth_token: str


class AWSInfraTriggerOperationRequest(BaseModel):
    canarytoken: str
    auth_token: str
    external_id: Optional[str] = None


class AWSInfraHandleRequest(BaseModel):
    handle: str


class AWSInfraGenerateDataChoiceRequest(BaseModel):
    canarytoken: str
    auth_token: str
    asset_type: AWSInfraAssetType
    asset_field: AWSInfraAssetField
    parent_asset_name: Optional[str] = None
    plan: Optional[dict] = None


class AWSInfraSavePlanRequest(BaseModel):
    canarytoken: str
    auth_token: str
    plan: Any


class AWSInfraManagementResponseRequest(BaseModel):
    handle: str
    operation: AWSInfraOperationType
    result: dict


class AWSInfraGenerateChildAssetsRequest(BaseModel):
    canarytoken: str
    auth_token: str
    assets: dict[
        Union[
            Literal[AWSInfraAssetType.S3_BUCKET],
            Literal[AWSInfraAssetType.DYNAMO_DB_TABLE],
        ],
        list[str],
    ]


class AWSInfraTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    aws_account_number: str
    aws_region: str


class AWSInfraTokenEditRequest(TokenEditRequest):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    aws_account_number: Optional[str]
    aws_region: Optional[str]


class AWSInfraConfigStartResponse(BaseModel):
    result: bool
    message: str = ""
    role_setup_commands: dict


class AWSInfraHandleResponse(BaseModel):
    handle: str
    message: str = ""
    error: str = ""


class AWSInfraCheckRoleReceivedResponse(BaseModel):
    result: bool
    message: str = ""
    handle: str
    session_credentials_retrieved: bool
    error: str = ""


class AWSInfraInventoryCustomerAccountReceivedResponse(BaseModel):
    result: bool
    message: str = ""
    handle: str
    proposed_plan: dict = {}
    error: str = ""
    data_generation_remaining: int = 0


class AWSInfraGenerateDataChoiceResponse(BaseModel):
    result: bool
    message: str = ""
    proposed_data: Optional[str] = None
    data_generation_remaining: int = 0


class AWSInfraSavePlanResponse(BaseModel):
    result: bool
    message: str = ""
    terraform_module_source: str = ""


class AWSInfraSetupIngestionReceivedResponse(BaseModel):
    result: bool
    message: str = ""
    handle: str
    terraform_module_snippet: Optional[dict] = None
    role_cleanup_commands: Optional[dict] = None
    error: str = ""


class AWSInfraTeardownReceivedResponse(BaseModel):
    result: bool
    message: str = ""
    handle: str
    role_cleanup_commands: Optional[dict] = None
    error: str = ""


class AWSInfraGenerateChildAssetsResponse(BaseModel):
    assets: dict[
        Union[
            Literal[AWSInfraAssetType.S3_BUCKET],
            Literal[AWSInfraAssetType.DYNAMO_DB_TABLE],
        ],
        dict[str, list[str]],
    ]
    data_generation_remaining: int = 0


class AWSInfraTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    aws_region: str
    aws_account_number: str
    tf_module_prefix: str
    ingesting: bool


class AwsInfraAdditionalInfo(BaseModel):
    event: Optional[dict[str, Any]]
    decoy_resource: Optional[dict[str, Any]]
    identity: Optional[dict[str, Any]]
    metadata: Optional[dict[str, Any]]

    def serialize_for_v2(self) -> dict:
        return self.dict()


class AWSInfraTokenHit(TokenHit):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    input_channel: str = "HTTP"
    additional_info: Optional[AwsInfraAdditionalInfo]

    def serialize_for_v2(self) -> dict:
        return json_safe_dict(self, exclude=("token_type", "time_of_hit"))


class AWSInfraTokenHistory(TokenHistory[AWSInfraTokenHit]):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    hits: List[AWSInfraTokenHit] = []
