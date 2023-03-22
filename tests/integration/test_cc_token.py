import os
from distutils.util import strtobool
from typing import Union

import pytest

# import requests
# from pydantic import HttpUrl

from canarytokens.models import (
    V2,
    V3,
    # CCTokenHistory,
    # CCTokenRequest,
    # CCTokenResponse,
    # DownloadIncidentListJsonRequest,
    # Memo,
    # TokenTypes,
)

# from tests.utils import aws_token_fire, create_token
# from tests.utils import get_token_history as utils_get_token_history
from tests.utils import v2, v3  # , run_or_skip


@pytest.mark.parametrize("version", [v2, v3])
@pytest.mark.skipif(
    (
        strtobool(os.getenv("SKIP_CC_TEST", "True"))
        or not strtobool(os.getenv("LIVE", "False"))
    ),
    reason="avoid using up a CC each time we run tests, and AWS can't trigger unless live",
)
def test_cc_token(version: Union[V2, V3]):
    pass
