import os
import subprocess
from distutils.util import strtobool
from os import remove
from pathlib import Path
from time import sleep
from typing import Union

import pytest
from pydantic import HttpUrl
from requests import get

from canarytokens.canarydrop import Canarydrop
from canarytokens.models import (
    V2,
    V3,
    Memo,
    MySQLTokenHistory,
    MySQLTokenRequest,
    MySQLTokenResponse,
)
from canarytokens.mysql import make_canary_mysql_dump
from canarytokens.settings import BackendSettings, Settings
from tests.utils import create_token, get_token_history, run_or_skip, v2, v3

backend_settings = BackendSettings(
    _env_file=f"{os.path.realpath('.')}/backend/backend.env"
)
switchboard_settings = Settings(
    _env_file=f"{os.path.realpath('.')}/backend/{backend_settings.SWITCHBOARD_SETTINGS_PATH}"
)


@pytest.mark.parametrize("version", [v2, v3])
def test_mysql_token(
    version: Union[V2, V3],
    webhook_receiver: str,
    backend_settings: BackendSettings,
    runv2: bool,
    runv3: bool,
):
    run_or_skip(version, runv2=runv2, runv3=runv3)
    token_request = MySQLTokenRequest(
        webhook_url=HttpUrl(url=webhook_receiver, scheme="https"),
        memo=Memo("Test stuff break stuff test stuff sometimes build stuff"),
    )
    resp = create_token(token_request, version=version)
    token_info = MySQLTokenResponse(**resp)
    gz_file = f"{token_info.token}_mysql_dump.sql.gz"
    if version.live:
        url = f"{version.server_url}/download?fmt=my_sql&token={token_info.token}&auth={token_info.auth_token}&encoded=true"
        with get(url) as rc:
            with open(gz_file, "wb") as f:
                f.write(rc.content)
    else:
        if isinstance(version, V3):
            assert token_info.usage is not None
            assert token_info.usage[-8:] == "REPLICA;"
        listen_domain = os.getenv("TEST_HOST", "app")
        content = make_canary_mysql_dump(
            mysql_usage=Canarydrop.generate_mysql_usage(
                token=token_info.token,
                domain=listen_domain,
                port=switchboard_settings.CHANNEL_MYSQL_PORT,
                encoded=switchboard_settings.CHANNEL_MYSQL_PORT,
            ),
            template=Path(backend_settings.TEMPLATES_PATH) / "mysql_tables.zip",
        )
        with open(gz_file, "wb") as f:
            f.write(content)
    _ = subprocess.run(["gzip", "-d", gz_file], capture_output=True)
    dump_file = gz_file[:-3]

    # Trigger the token
    command = ["mysql", "-h127.0.0.1", "-uroot"]
    if not strtobool(os.getenv("CI", "False")):
        command[command.index("-h127.0.0.1")] = "-hmysql"

    command_input = bytes(
        f"drop database IF EXISTS tmp_db; create database tmp_db; use tmp_db; source {dump_file}; drop database IF EXISTS tmp_db;",
        "utf-8",
    )
    stuff = subprocess.run(command, input=command_input, capture_output=True)
    print(f"\nmysql: {stuff}")
    remove(dump_file)

    # the v3 backend in docker runs slower than this test,
    # so we need to wait to let it save the hit before requesting it
    if isinstance(version, V3):
        sleep(1)

    # Check that the returned history has a hit
    history_resp = get_token_history(token_info, version=version)
    token_history = MySQLTokenHistory(**history_resp)

    if isinstance(version, V2):
        assert len(token_history.hits) >= 1
    else:
        assert len(token_history.hits) == 1
