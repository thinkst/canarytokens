import random
import secrets
import string


def _random_alpha_numeric_string(length: int, lower_case_only=False) -> str:
    """
    Generate a random string of fixed length.
    """
    if lower_case_only:
        characters = string.ascii_lowercase + string.digits
    else:
        characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


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
