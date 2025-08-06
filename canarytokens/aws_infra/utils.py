import random
import re
import secrets
import string

S3_BUCKET_NAME_REGEX = re.compile(
    r"^(?!\d{1,3}(\.\d{1,3}){3}$)[a-z0-9][a-z0-9\.\-]{1,61}[a-z0-9]$"
)
DYNAMO_DB_TABLE_NAME_REGEX = re.compile(r"[A-Za-z0-9_.\-]{3,255}")
SSM_PARAMETER_NAME_REGEX = re.compile(r"[A-Za-z0-9_.\-]+")
SQS_QUEUE_NAME_REGEX = re.compile(r"[A-Za-z0-9_\-;]{1,80}")
SECRETS_MANAGER_NAME_REGEX = re.compile(r"(?!.*\.\.)[A-Za-z0-9/_+=\.@\-]{1,512}")
S3_OBJECT_REGEX = re.compile(r"^[a-zA-Z0-9\-\._~!$&'()*+,;=:@/]{1,1024}$")
TABLE_ITEM_REGEX = re.compile(r"^[a-zA-Z0-9\-\._~!$&'()*+,;=:@/]{1,1024}$")


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
