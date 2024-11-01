import os
import subprocess
import tempfile
from typing import Literal, Union

import pytest

from canarytokens.models import (
    Memo,
    SQLServerTokenHistory,
    SQLServerTokenRequest,
    SQLServerTokenResponse,
    TokenTypes,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric
from tests.utils import create_token, get_stats_from_webhook, get_token_history, v2


@pytest.mark.skipif(os.name != "nt", reason="Requires nt os (Windows OS)")
@pytest.mark.parametrize(
    "version, table, view, procedure, trigger, event",
    [
        (
            v2,
            "table_name_insert",
            "view_name_insert",
            "ping_canarytokens_insert",
            "trigger_name_insert",
            "insert",
        ),
        (
            v2,
            "table_name_delete",
            "view_name_delete",
            "ping_canarytokens_delete",
            "trigger_name_delete",
            "delete",
        ),
        (
            v2,
            "table_name_update",
            "view_name_update",
            "ping_canarytokens_update",
            "trigger_name_update",
            "update",
        ),
        (
            v2,
            "table_name_select",
            "view_name_select",
            "ping_canarytokens_select",
            "trigger_name_select",
            "select",
        ),
        # v3,
    ],
)
def test_sql_server_token(
    version,
    table: str,
    view: str,
    procedure: str,
    trigger: str,
    event: Union[
        Literal["insert"], Literal["delete"], Literal["update"], Literal["select"]
    ],
    webhook_receiver,
):

    # initialize request
    memo = "testing sql_server_token"
    token_request = SQLServerTokenRequest(
        token_type=TokenTypes.SQL_SERVER,
        sql_server_table_name=table,
        sql_server_view_name=view,
        sql_server_function_name=procedure,
        sql_server_trigger_name=trigger,
        webhook_url=webhook_receiver,
        memo=Memo(memo),
    )

    # Create sql server token
    resp = create_token(token_request=token_request, version=version)
    token_info = SQLServerTokenResponse(**resp)

    # sql database variables for sql scripts
    sql_database_variables = {
        "token": token_info.hostname,
        "table": table,
        "procedure": procedure,
        "trigger": trigger,
        "view": view,
    }

    # extract sql script template
    script_template = f"tests\\data\\sql_server_token_{event}_script.txt"
    with open(script_template, "r") as fp:
        script = fp.read()

    # create temporary directory and sql script
    script_file_name = "sql_server_token_script.sql"
    tmpdir = tempfile.mkdtemp()
    script_file = "{tmpdir}\\{file}".format(tmpdir=tmpdir, file=script_file_name)
    with open(script_file, "w") as fp:
        fp.write(script.format(**sql_database_variables))

    # Trigger the token
    proc = subprocess.Popen(
        [
            "sqlcmd",
            "-S",
            "localhost",
            "-U",
            "sa",
            "-P",
            "dbatools.I0",
            "-d",
            "tempdb",
            "-i",
            f"{script_file}",
        ],
        stdout=subprocess.PIPE,
    )

    # capture output
    sqlcmd_out = proc.communicate()[0]

    # check sqlcmd output
    assert b"rows affected" in sqlcmd_out

    # Check that the returned history has a atleast a single hit
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    resp = get_token_history(token_info=token_info, version=version)
    token_history = SQLServerTokenHistory(**resp)
    assert len(token_history.hits) >= 1
    if len(token_history.hits) >= 1:
        token_hit = token_history.hits[0]
        assert token_hit.input_channel == "DNS"
