import logging
import random
import re
import secrets
import string
import httpx

from attr import dataclass
from typing import Optional

from canarytokens.settings import FrontendSettings

settings = FrontendSettings()

log = logging.getLogger()

AWS_INFRA_ENABLED = (
    settings.AWS_INFRA_AWS_ACCOUNT
    and settings.AWS_INFRA_AWS_REGION
    and settings.AWS_INFRA_SHARED_SECRET
    and settings.AWS_INFRA_MANAGEMENT_REQUEST_SQS_URL
    and settings.AWS_INFRA_CALLBACK_DOMAIN
    and settings.AWS_INFRA_INGESTION_BUS
    and settings.AWS_INFRA_TF_MODULE_BUCKET
)
S3_BUCKET_NAME_REGEX = re.compile(
    r"^(?!\d{1,3}(\.\d{1,3}){3}$)[a-z0-9][a-z0-9\.\-]{1,61}[a-z0-9]$"
)
DYNAMO_DB_TABLE_NAME_REGEX = re.compile(r"[A-Za-z0-9_.\-]{3,255}")
SSM_PARAMETER_NAME_REGEX = re.compile(r"[A-Za-z0-9_.\-]{1,1011}")
SQS_QUEUE_NAME_REGEX = re.compile(r"[A-Za-z0-9_\-;]{1,80}")
SECRETS_MANAGER_NAME_REGEX = re.compile(r"(?!.*\.\.)[A-Za-z0-9/_+=\.@\-]{1,512}")
S3_OBJECT_REGEX = re.compile(r"^[a-zA-Z0-9\-\._~!$&'()*+,;=:@/]{1,1024}$")
TABLE_ITEM_REGEX = re.compile(r"^[a-zA-Z0-9\-\._~!$&'()*+,;=:@/]{1,1024}$")


@dataclass
class AssetNameValidation:
    result: bool
    error_message: Optional[str] = None


def _random_alpha_numeric_string(length: int, lower_case_only=False) -> str:
    """
    Generate a random string of fixed length.
    """
    if lower_case_only:
        characters = string.ascii_lowercase + string.digits
    else:
        characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


def _secret_alpha_numeric_string(length: int) -> str:
    """
    Generate a random string of fixed length using secrets module.
    """
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def generate_external_id():
    return _secret_alpha_numeric_string(21)


def generate_tf_module_prefix():
    return _random_alpha_numeric_string(27)


def generate_inventory_role_name():
    """
    Generate a unique inventory role name for the canarydrop.
    """
    return f"Canarytokens-Inventory-{_random_alpha_numeric_string(10)}-ReadOnly-Role"


def generate_handle_id():
    return secrets.token_hex(20)


def generate_s3_bucket_suffix():
    """
    Generate a random suffix for S3 bucket names.
    """
    return _random_alpha_numeric_string(random.randint(6, 21), lower_case_only=True)


def generate_content():
    """
    Generate random content for S3 objects.
    """
    return _random_alpha_numeric_string(random.randint(5, 1000))


async def s3_bucket_is_available(bucket_name: str) -> bool:
    """
    Check if an S3 bucket is available.
    """
    url = f"https://{bucket_name}.s3.amazonaws.com"

    # Fall back to deprecated path-style access if the bucket name contains period
    #
    # AWS doesn't fully support testing bucket existence via virtual-hosted-style URLs if the bucket
    # name contains a . in it. Those HTTPS requests fail TLS verification as the wildcard in the
    # TLS certificate (*.s3.amazonaws.com) only supports a single subdomain. While this changes the
    # HTTP response codes returned, 404 for non-existent bucket is consistent for both styles
    if "." in bucket_name:
        url = f"https://s3.eu-west-1.amazonaws.com/{bucket_name}"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.head(url)
        return (
            response.status_code == 404
        )  # Not Found indicates the bucket does not exist
    except Exception:
        log.exception("Error checking S3 bucket existence")
        return False


def validate_s3_name(name: str) -> AssetNameValidation:
    """Validate S3 bucket name asynchronously."""
    if not re.fullmatch(S3_BUCKET_NAME_REGEX, name):
        return AssetNameValidation(
            result=False,
            error_message=f"S3 bucket names must be 3-63 characters, lowercase letters, numbers, dots, and hyphens only: {name}",
        )
    reserved_prefixes = (
        "xn--",
        "sthree-",
        "sthree-configurator",
        "s3alias",
        "s3-",
        "s3control-",
    )
    reserved_suffixes = ("--ol-s3",)
    if any(name.startswith(p) for p in reserved_prefixes) or any(
        name.endswith(s) for s in reserved_suffixes
    ):
        return AssetNameValidation(
            result=False,
            error_message=f"S3 bucket name cannot start with reserved prefixes or end with reserved suffixes: {name}",
        )

    return AssetNameValidation(result=True)


def validate_dynamodb_name(name: str) -> AssetNameValidation:
    if re.fullmatch(DYNAMO_DB_TABLE_NAME_REGEX, name):
        return AssetNameValidation(result=True)
    return AssetNameValidation(
        result=False,
        error_message=f"DynamoDB table name must be 3-255 characters, alphanumeric, underscore, dot, hyphen only: {name}",
    )


def validate_ssm_parameter_name(name: str) -> AssetNameValidation:
    if name.lower().startswith(("aws", "ssm")):
        return AssetNameValidation(
            result=False,
            error_message=f"SSM parameter name cannot start with reserved prefixes: {name}",
        )
    if re.fullmatch(SSM_PARAMETER_NAME_REGEX, name):
        return AssetNameValidation(result=True)
    return AssetNameValidation(
        result=False,
        error_message=f"SSM parameter names must be alphanumeric, underscore, dot, hyphen only: {name}",
    )


def validate_sqs_name(name: str) -> AssetNameValidation:
    if re.fullmatch(SQS_QUEUE_NAME_REGEX, name):
        return AssetNameValidation(result=True)
    return AssetNameValidation(
        result=False,
        error_message=f"SQS queue name must be 1-80 characters, alphanumeric, underscore, hyphen, semicolon only: {name}",
    )


def validate_secrets_manager_name(name: str) -> AssetNameValidation:
    if re.fullmatch(SECRETS_MANAGER_NAME_REGEX, name):
        return AssetNameValidation(result=True)
    return AssetNameValidation(
        result=False,
        error_message=f"Secrets Manager name must be 1-512 characters, alphanumeric, underscore, dot, hyphen, equal, plus, at only, no consecutive dots: {name}",
    )
