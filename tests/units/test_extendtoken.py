import os

import pytest

from canarytokens import extendtoken
from canarytokens.settings import FrontendSettings
from canarytokens.utils import strtobool

settings = FrontendSettings("../frontend/frontend.env")


@pytest.mark.skipif(
    not strtobool(os.getenv("MAKE_CARD", "False")),
    reason="We don't want to use up a cc every time we run tests",
)
def test_create_cc():
    eapi = extendtoken.ExtendAPI(
        email=settings.EXTEND_EMAIL,
        password=settings.EXTEND_PASSWORD.get_secret_value(),
        card_name=settings.EXTEND_CARD_NAME,
    )
    token_url = "http://canarytokens.com/static/tags/traffic/u27uxknlv3x2wzpe5ufkehpmh/contact.php"
    cc = eapi.create_credit_card(token_url=token_url)
    assert len(cc.number) == 15
