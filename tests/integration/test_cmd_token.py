import random
import pytest

from canarytokens.constants import CANARYTOKEN_ALPHABET
from canarytokens import msreg
from canarytokens.models import (
    CMDTokenHistory,
    CMDTokenRequest,
    CMDTokenResponse,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric

from tests.utils import (
    clear_stats_on_webhook,
    trigger_cmd_token,
    create_token,
    get_stats_from_webhook,
    get_token_history,
)


@pytest.mark.parametrize(
    "use_invocation_id, expected_hits",
    [
        (True, 1),
        (False, 2),
    ],
)
def test_cmd_token_fires(
    use_invocation_id: bool,
    expected_hits: int,
    webhook_receiver,
    version,
):
    """
    Tests the sensitive command token.
    """

    # Create a CMD token request
    memo = "Test stuff break stuff test stuff sometimes build stuff"

    token_request = CMDTokenRequest(
        webhook_url=webhook_receiver, memo=memo, cmd_process="klist.exe"
    )
    resp = create_token(token_request)

    # Check dns token has correct attributes
    token_info = CMDTokenResponse(**resp)
    # assert dns_token_info.webhook_url == token_request.webhook_url
    assert token_info.token in token_info.hostname.split(".")

    clear_stats_on_webhook(webhook_receiver, token=token_info.token)
    # Trigger CMD token twice, make sure the invocation ID limits it to one hit
    invocation_id = (
        "".join(
            random.choice(CANARYTOKEN_ALPHABET)
            for _ in range(msreg.INVOCATION_ID_LENGTH)
        )
        if use_invocation_id
        else None
    )
    _ = trigger_cmd_token(token_info, invocation_id=invocation_id)
    _ = trigger_cmd_token(token_info, invocation_id=invocation_id)

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats is not None:
        # Check that the webhook was alerted
        assert len(stats) >= 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    # Check that the returned history has a single hit.
    resp = get_token_history(token_info=token_info)

    token_history = CMDTokenHistory(**resp)
    # TODO: what other fields do we want to assert on.
    #       note: making them TokenHistory have stronger validators is
    #             the better option.
    assert len(token_history.hits) == expected_hits
