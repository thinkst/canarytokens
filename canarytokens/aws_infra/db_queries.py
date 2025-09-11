from canarytokens.canarydrop import Canarydrop
from canarytokens.redismanager import DB
from datetime import timedelta

import json

from canarytokens.settings import FrontendSettings


settings = FrontendSettings()
INVENTORY_EXPIRY = timedelta(hours=3).seconds  # 3 hours


def _inventory_key(canarydrop: Canarydrop):
    return f"{canarydrop.canarytoken.value()}_aws_inventoried_assets"


def _data_generation_requests_key(canarydrop: Canarydrop):
    return f"{canarydrop.canarytoken.value()}_data_generation_requests"


def get_current_assets(canarydrop: Canarydrop) -> dict:
    """
    Retrieve the current assets inventoried for a given canarydrop.
    Returns an empty dict if no assets are found.
    :param canarydrop: The canarydrop instance for which to retrieve assets.
    """
    with DB.get_db() as r:
        return json.loads(r.get(_inventory_key(canarydrop)) or "{}")


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


def get_data_generation_requests(canarydrop: Canarydrop) -> int:
    with DB.get_db() as r:
        count = r.get(_data_generation_requests_key(canarydrop)) or 0
        return int(count)


def update_data_generation_requests(canarydrop: Canarydrop, count: int):
    def update(pipe):
        current_request_count = pipe.get(_data_generation_requests_key(canarydrop)) or 0
        pipe.multi()
        new_request_count = min(
            current_request_count + count, settings.AWS_INFRA_NAME_GENERATION_LIMIT
        )
        pipe.set(_data_generation_requests_key(canarydrop), new_request_count)

    with DB.get_db() as r:
        r.transaction(update, _data_generation_requests_key(canarydrop))
