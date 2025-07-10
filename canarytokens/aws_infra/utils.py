import random
import secrets
import string


def _random_string(length: int) -> str:
    """
    Generate a random string of fixed length.
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def _secret_string(length: int) -> str:
    """
    Generate a random string of fixed length using secrets module.
    """
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def generate_external_id():
    return _secret_string(21)


def generate_tf_module_prefix():
    return _random_string(27)


def generate_inventory_role_name():
    """
    Generate a unique inventory role name for the canarydrop.
    """
    return f"Canarytokens-Inventory-{_random_string(10)}-ReadOnly-Role"


def generate_handle_id():
    return _secret_string(20)
