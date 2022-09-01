from __future__ import annotations

import pytest

from canarytokens import canarydrop
from canarytokens.exceptions import NoCanarytokenFound
from canarytokens.models import TokenTypes
from canarytokens.queries import get_canarydrop, save_canarydrop
from canarytokens.redismanager import DB
from canarytokens.tokens import Canarytoken

pytestmark = pytest.mark.usefixtures("setup_db")


def test_ping():

    db = DB.get_db()
    db2 = DB.get_db()
    assert db is db2
    assert db.ping()


@pytest.mark.parametrize("token_type", [o for o in TokenTypes])
def test_canarydrop(token_type):
    canarytoken = Canarytoken()
    # FIXME: Add a fixture to load expected values from a settings obj

    cd = canarydrop.Canarydrop(
        type=token_type,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    save_canarydrop(cd)
    cd_retrieved = get_canarydrop(canarytoken)
    assert cd_retrieved.memo == cd.memo
    assert cd_retrieved.canarytoken.value() == cd.canarytoken.value()
    if cd_retrieved.type in [TokenTypes.SLOW_REDIRECT, TokenTypes.FAST_REDIRECT]:
        assert cd_retrieved.redirect_url == "https://youtube.com"


def test_not_found_token():
    with pytest.raises(NoCanarytokenFound):
        Canarytoken.find_canarytoken("not_in_db")


@pytest.mark.parametrize("token_type", [o for o in TokenTypes])
def test_canarydrop_auth(token_type):
    canarytoken = Canarytoken()
    # FIXME: Add a fixture to load expected values from a settings obj

    cd = canarydrop.Canarydrop(
        type=token_type,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    save_canarydrop(cd)

    cd_2 = canarydrop.Canarydrop(
        type=token_type,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    save_canarydrop(cd_2)
    assert cd.auth != cd_2.auth
