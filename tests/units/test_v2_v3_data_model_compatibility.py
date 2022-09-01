import json
from pathlib import Path

import pytest
from deepdiff import DeepDiff

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.redismanager import DB
from canarytokens.tokens import Canarytoken

allowed_attrs = [
    "alert_email_enabled",
    "alert_email_recipient",
    "alert_sms_enabled",
    "alert_sms_recipient",
    "alert_webhook_enabled",
    "alert_webhook_url",
    "canarytoken",
    "triggered_count",
    "triggered_list",
    "memo",
    "generated_url",
    "generated_email",
    "generated_hostname",
    "timestamp",
    "user",
    "imgur_token",
    "imgur",
    "auth",
    "browser_scanner_enabled",
    "web_image_path",
    "web_image_enabled",
    "type",
    "clonedsite",
    "aws_secret_access_key",
    "aws_access_key_id",
    "redirect_url",
    "region",
    "output",
    "slack_api_key",
    "wg_key",
    "kubeconfig",
    "generate",
]


@pytest.mark.parametrize(
    "data_file", [o for o in Path("tests/data/v2_drops").rglob("*.json")]
)
def test_triggered_details_vs_list(setup_db_connection_only, data_file):
    """V2 stores `triggered_list` holding all the token hit information.
    V3 stores `triggered_details` holding the same information in a slightly
    different shape.

    This test checks v3 can load v2 shaped data.
    """
    # Setup by adding v2 drop to redis
    with open(data_file, "r") as fp:
        data = json.load(fp)
    DB.get_db().hset(f"{data_file.stem[:-3]}xxx", mapping=data)

    # Check fetching the drop works
    drop = queries.get_canarydrop_triggered_details(
        Canarytoken(f"{data_file.stem[:-3]}xxx")
    )
    # Check trigger_list is consistent with hits:list
    trigger_list = json.loads(data.get("triggered_list", "{}"))
    assert len(drop.hits) == len(trigger_list)

    assert (
        set([float(o) for o in trigger_list.keys()])
        - set([h.time_of_hit for h in drop.hits])
        == set()
    )

    # clean up
    DB.get_db().delete(f"{data_file.stem[:-3]}xxx")


@pytest.mark.parametrize(
    "data_file", sorted([o for o in Path("tests/data/v2_drops/").rglob("*.json")])
)
def test_loading_drops(setup_db_connection_only, data_file):
    """
    Ensures Redis drop structure is unchanged when loaded, stored by
    the v3 implementation.
    Note: when loading the tokens a suffix of xxx is added to the
    drop key to so we don't nuke the original value.
    """

    # Setup by adding v2 drop to redis
    with open(data_file, "r") as fp:
        data = json.load(fp)
        data["canarytoken"] = f"{data['canarytoken'][:-3]}xxx"
    DB.get_db().delete(f"{data_file.stem[:-3]}xxx")
    DB.get_db().hset(f"{data_file.stem[:-3]}xxx", mapping=data)
    # Check fetching the drop works
    drop: Canarydrop = queries.get_canarydrop(Canarytoken(f"{data_file.stem[:-3]}xxx"))

    assert str(drop.alert_webhook_url) == data["alert_webhook_url"]
    assert str(drop.alert_email_recipient) == data["alert_email_recipient"]
    assert drop.canarytoken.value() == data["canarytoken"]
    assert str(drop.type) == data["type"]

    # Remove drop from redis
    DB.get_db().delete(f"{data_file.stem[:-3]}xxx")
    # Save drop which serializes it and stores it in redis
    queries.save_canarydrop(drop)
    # reload_drop which deserializes it.
    reloaded_drop: Canarydrop = queries.get_canarydrop(
        Canarytoken(f"{data_file.stem[:-3]}xxx")
    )

    def get_canarydrop(canarytoken):
        canarydrop = DB.get_db().hgetall(canarytoken)
        if "triggered_list" in canarydrop.keys():
            canarydrop["triggered_list"] = json.loads(canarydrop["triggered_list"])
        return canarydrop

    v2_canarydrop = get_canarydrop(canarytoken=f"{data_file.stem[:-3]}xxx")

    assert set(v2_canarydrop.keys()) - set(allowed_attrs) == set()

    # Check drops are identical
    assert DeepDiff(reloaded_drop, drop, exclude_types=[Path]) == {}
    assert reloaded_drop == drop

    # Grab the drop from redis as a dict
    reloaded_data = DB.get_db().hgetall(f"{data_file.stem[:-3]}xxx")
    # Check data is unchanged
    if "triggered_list" in data:
        # Compare triggered_list separately as order of keys
        reloaded_list = json.loads(reloaded_data.pop("triggered_list"))
        original_list = json.loads(data.pop("triggered_list"))

        assert (
            DeepDiff(
                reloaded_list,
                original_list,
                exclude_types=[type(None)],
            )
            == {}
        )
    assert reloaded_data == data
    assert DeepDiff(reloaded_data, data) == {}
    # clean up
    DB.get_db().delete(f"{data_file.stem[:-3]}xxx")


def test_dump_v2_drops(setup_db_connection_only):
    """Easy way to create v2 data files."""
    pytest.skip()
    # counter = Counter()
    data_path = Path("tests/data/v2_tmp")
    for key in DB.get_db().scan_iter("canarydrop:*"):
        data = DB.get_db().hgetall(key)
        if not data.get("type", False):
            continue
        if data["type"] == "aws_keys":
            if "safe" in data.get("triggered_list", ""):
                # if counter[data["type"]] < 20:
                #     counter.update([data["type"]])
                (data_path / f"{data['type']}").mkdir(exist_ok=True, parents=True)
                with open(data_path / f"{data['type']}/{key}.json", "w") as fp:
                    json.dump(data, fp)
