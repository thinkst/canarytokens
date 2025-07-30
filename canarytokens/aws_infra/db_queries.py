from canarytokens.canarydrop import Canarydrop
from canarytokens.redismanager import DB
from datetime import timedelta

import json

INVENTORY_EXPIRY = timedelta(hours=3).seconds  # 3 hours


def _inventory_key(canarydrop: Canarydrop):
    return f"{canarydrop.canarytoken.value()}_aws_inventoried_assets"


def get_current_assets(canarydrop: Canarydrop) -> dict:
    """
    Retrieve the current assets inventoried for a given canarydrop.
    Returns an empty dict if no assets are found.
    :param canarydrop: The canarydrop instance for which to retrieve assets.
    """
    with DB.get_db() as r:
        return json.loads(r.get(_inventory_key(canarydrop))) or {}


def save_current_assets(canarydrop: Canarydrop, assets: dict) -> None:
    """
    Save the current assets inventoried for a given canarydrop.
    :param canarydrop: The canarydrop instance for which to save assets.
    :param assets: The inventoried assets to save.
    """
    with DB.get_db() as r:
        r.set(_inventory_key(canarydrop), json.dumps(assets), ex=INVENTORY_EXPIRY)


def delete_current_assets(canarydrop: Canarydrop) -> None:
    """
    Delete the current assets inventoried for a given canarydrop.
    :param canarydrop: The canarydrop instance for which to delete assets.
    """
    with DB.get_db() as r:
        r.delete(_inventory_key(canarydrop))


def update_data_generation_usage(canarydrop: Canarydrop, requests: int) -> None:
    """
    Update the data generation usage for a given canarydrop.
    :param canarydrop: The canarydrop instance for which to update usage.
    :param requests: The number of requests to add to the usage.
    """
    with DB.get_db() as r:
        key = f"{canarydrop.canarytoken.value()}_data_generation_usage"
        current_usage = r.get(key)
        if current_usage is None:
            current_usage = 0
        else:
            current_usage = int(current_usage)
        r.set(
            key, current_usage + requests, ex=INVENTORY_EXPIRY
        )  # Reset expiry on update
