import re
from functools import partial
from smtplib import SMTP
from typing import Union

import pytest
import requests
from pydantic import HttpUrl

from canarytokens.exceptions import CanaryTokenCreationError
from canarytokens.models import (
    V2,
    V3,
    ClonedWebTokenHistory,
    ClonedWebTokenRequest,
    ClonedWebTokenResponse,
    DNSTokenHistory,
    DNSTokenRequest,
    DNSTokenResponse,
    FastRedirectTokenHistory,
    FastRedirectTokenRequest,
    FastRedirectTokenResponse,
    Log4ShellTokenHistory,
    Log4ShellTokenRequest,
    Log4ShellTokenResponse,
    Memo,
    SlowRedirectTokenHistory,
    SlowRedirectTokenRequest,
    SlowRedirectTokenResponse,
    SMTPTokenHistory,
    SMTPTokenRequest,
    SMTPTokenResponse,
    TokenAlertDetailGeneric,
    WebBugTokenHistory,
    WebBugTokenRequest,
    WebBugTokenResponse,
    WindowsDirectoryTokenHistory,
    WindowsDirectoryTokenRequest,
    WindowsDirectoryTokenResponse,
)
from canarytokens.settings import Settings
from tests.utils import (
    clear_stats_on_webhook,
    create_token,
    get_stats_from_webhook,
    get_token_history,
    log_4_shell_fire_token,
    plain_fire_token,
    run_or_skip,
    slack_webhook_test,
    trigger_http_token,
    v2,
    v3,
    windows_directory_fire_token,
)


@pytest.mark.parametrize("version", [None])
def test_basic_v3(version, runv3, runv2):  # pragma: no cover
    run_or_skip(version, runv2=runv2, runv3=runv3)
    token_request = DNSTokenRequest(
        webhook_url=slack_webhook_test,
        memo="We are v3",
    )
    resp = create_token(token_request, version=version)

    # Check dns token has correct attributes
    token_info = DNSTokenResponse(**resp)
    # assert dns_token_info.webhook_url == token_request.webhook_url
    assert token_info.hostname.split(".")[0] == token_info.token

    # Trigger DNS token
    _ = plain_fire_token(token_info, version=version)

    # Check that the returned history has a single hit.
    resp = get_token_history(token_info=token_info, version=version)

    token_history = DNSTokenHistory(**resp)

    # TODO: what other fields do we want to assert on.
    #       note: makeing them TokenHistory have stronger validators is
    #             the better option.
    assert len(token_history.hits) == 1


@pytest.mark.parametrize(
    "version, token_request_type, token_response_type, token_history_type, token_trigger",
    [
        (v3, DNSTokenRequest, DNSTokenResponse, DNSTokenHistory, plain_fire_token),
        (
            v3,
            WindowsDirectoryTokenRequest,
            WindowsDirectoryTokenResponse,
            WindowsDirectoryTokenHistory,
            partial(windows_directory_fire_token, domain="username.hostname.domain"),
        ),
        (
            v3,
            Log4ShellTokenRequest,
            Log4ShellTokenResponse,
            Log4ShellTokenHistory,
            partial(log_4_shell_fire_token, retrieved_hostname="somehostname.local"),
        ),
        (v2, DNSTokenRequest, DNSTokenResponse, DNSTokenHistory, plain_fire_token),
        (
            v2,
            Log4ShellTokenRequest,
            Log4ShellTokenResponse,
            Log4ShellTokenHistory,
            partial(log_4_shell_fire_token, retrieved_hostname="somehostname.local"),
        ),
        (
            v2,
            WindowsDirectoryTokenRequest,
            WindowsDirectoryTokenResponse,
            WindowsDirectoryTokenHistory,
            plain_fire_token,
        ),
    ],
)
def test_dns_triggered_tokens(
    webhook_receiver,
    version,
    token_request_type,
    token_response_type,
    token_history_type,
    token_trigger,
    runv2,
    runv3,
):
    """
    Tests all tokens that are triggered via the DNS channel. It's a fully `parametrize`'d
    test and covers just the basics.

    Currently runs: dns, log4shell, windows_directory

    If more specialized tests are needed for a particular token type then
    add those as a separate test. That is advisable over making this complex test even more
    complex.
    """
    run_or_skip(version, runv2=runv2, runv3=runv3)
    # Create a DNS token request
    memo = "Test stuff break stuff test stuff sometimes build stuff"

    token_request = token_request_type(
        webhook_url=webhook_receiver,
        memo=memo,
    )
    resp = create_token(token_request, version=version)

    # Check dns token has correct attributes
    token_info = token_response_type(**resp)
    # assert dns_token_info.webhook_url == token_request.webhook_url
    assert token_info.hostname.split(".")[0] == token_info.token

    clear_stats_on_webhook(webhook_receiver, token=token_info.token)
    # Trigger DNS token
    _ = token_trigger(token_info, version=version)

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats is not None:
        # Check that what was sent to the webhook is consistent.
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])
    # Check that the returned history has a single hit.
    resp = get_token_history(token_info=token_info, version=version)

    token_history = token_history_type(**resp)
    # TODO: what other fields do we want to assert on.
    #       note: makeing them TokenHistory have stronger validators is
    #             the better option.
    assert len(token_history.hits) == 1


# @given(
#     hostname_to_retrieve=st.from_regex(
#         # REF: https://man7.org/linux/man-pages/man7/hostname.7.html
#         r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{4,8}[a-zA-Z0-9])\.){4,8}([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]{4,8}[A-Za-z0-9]){1,25}$"
#     ),
#     version=st.sampled_from([v3]),
# )
@pytest.mark.parametrize(
    "version, hostname_to_retrieve",
    [
        (v3, "testhost.name.com"),
        (v2, "testhost.name.com"),
    ],
)
def test_log_4_shell_token(
    version, hostname_to_retrieve, webhook_receiver, runv2, runv3
):
    """Tests the Log4Shell token. Creates a token with `webhook_receiver` as
    the output channel. Triggers the token with with `computer_name` as `hostname_to_retrieve`
    and checks that it is correctly recovered in the `src_data`.

    Args:
        version (Union[V2, V3]): indicates the server version we testing against.
        hostname_to_retrieve (str): computer_name that we want to recover based on how it's added to the token.
        webhook_receiver (str): A webhook reciever yto
    """
    run_or_skip(version, runv2=runv2, runv3=runv3)
    # Create a DNS token request
    memo = "Test stuff break stuff test stuff sometimes build stuff"

    dns_request = Log4ShellTokenRequest(
        webhook_url=webhook_receiver,
        memo=memo,
    )

    resp = create_token(dns_request, version=version)
    # Check dns token has correct attributes
    token_info = Log4ShellTokenResponse(**resp)
    assert token_info.hostname.split(".")[0] == token_info.token

    # Clear the webhook stats
    clear_stats_on_webhook(webhook_receiver, token=token_info.token)
    # Trigger the token
    hostname_to_retrieve = hostname_to_retrieve.strip()
    _ = log_4_shell_fire_token(
        token_info, retrieved_hostname=hostname_to_retrieve, version=version
    )

    # Check the webhook got correct number of triggers and correct info
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    # TODO: Gather these common blocks for webhook data checks and make them better.
    if stats is not None:
        # Check that what was sent to the webhook is consistent.
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        details_sent_to_webhook = TokenAlertDetailGeneric(**stats[0])
        assert (
            details_sent_to_webhook.additional_data["src_data"][
                "log4_shell_computer_name"
            ]
            == hostname_to_retrieve.lower()
        )

    # Get token history and check that it is consistent and correct.
    resp = get_token_history(token_info=token_info, version=version)
    token_history = Log4ShellTokenHistory(**resp)
    assert (
        token_history.hits[0].src_data["log4_shell_computer_name"].lower()
        == hostname_to_retrieve.lower()
    )


@pytest.mark.parametrize(
    "version,memo",
    [
        (v2, "V2 is email test"),
        (v3, "V3 email test run"),
    ],
)
def test_unique_email_token(
    version: Union[V2, V3],
    memo: str,
    webhook_receiver: str,
    runv2: bool,
    runv3: bool,
    settings: Settings,
):
    """
    Tests unique email token. Creates a token with random memo and triggers
    it by sending an email. Checks that the token history is consistent and the revovered
    details are correct.
    """
    run_or_skip(version, runv2=runv2, runv3=runv3)
    # Create SMTP token
    smtp_token_request = SMTPTokenRequest(
        webhook_url=webhook_receiver,
        memo=memo,
    )
    #
    resp = create_token(smtp_token_request, version=version)
    unique_email = resp.pop("unique_email", None)
    smtp_token_response = SMTPTokenResponse(**resp, unique_email=unique_email)

    clear_stats_on_webhook(webhook_receiver, token=smtp_token_response.token)
    # Trigger SMTP token
    sender = SMTP(
        host=version.canarytokens_domain,
        port=25 if version.live else int(settings.CHANNEL_SMTP_PORT),
    )
    # TODO: Add email attachment and test that is recovered.
    #       Add other fields we expect to recover.
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    message = MIMEMultipart()
    message["Subject"] = "Twisted is great!"
    message["From"] = "fromtest@test.com"
    message["To"] = ", ".join(["me@test.com", "you@test.com"])
    with open("tests/data/canary_image.png", mode="rb") as fp:
        part_image = MIMEImage(
            fp.read(),
        )
        # part.set_payload(fp.read())
    part_image.add_header(
        "content-disposition", "attachment", filename="canary_image.png"
    )
    link = "https://test.com/link"
    part_text = MIMEText(f"This is my super awesome email, link {link}", "plain")
    message.attach(part_text)
    message.attach(part_image)
    _ = sender.sendmail(
        from_addr="test@test.com",
        to_addrs=smtp_token_response.unique_email,
        msg=message.as_string(),
    )
    stats = get_stats_from_webhook(webhook_receiver, token=smtp_token_response.token)
    # Check that what was sent to the webhook is consistent.
    if stats is not None:
        # Check that what was sent to the webhook is consistent.
        assert len(stats) == 1
        details = TokenAlertDetailGeneric(**stats[0])
        mail_details = details.additional_data["mail"]
        assert details.memo == memo
        assert len(mail_details["links"]) == 1
        assert mail_details["links"] == [link]
        assert len(mail_details["attachments"]) == 3

    # Check that the returned history has a single hit.
    resp = get_token_history(token_info=smtp_token_response, version=version)

    token_history = SMTPTokenHistory(**resp)
    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "SMTP"  # TODO: input channel should be an enum
    if version.live:
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    else:
        assert token_hit.geo_info.ip == "127.0.0.1"


@pytest.mark.parametrize(
    "version",
    [v2, v3],
)
def test_web_bug_token(version: Union[V2, V3], webhook_receiver, runv2, runv3) -> None:
    """
    Tests: web_bug_token
    """
    run_or_skip(version, runv2=runv2, runv3=runv3)
    memo = "Testing Web Bug from V3 test suite "
    useragent = "python4 from the future"
    # Create a cloned web token request
    token_request = WebBugTokenRequest(
        webhook_url=webhook_receiver,
        # email = email,
        memo=memo,
    )
    resp = create_token(token_request, version=version)

    token_info = WebBugTokenResponse(**resp)

    # Trigger the token
    trigger_http_token(
        token_info=token_info, version=version, headers={"User-Agent": useragent}
    )

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)

    if stats is not None:
        # Check that what was sent to the webhook is consistent.
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        assert stats[0]["additional_data"]["useragent"] == useragent
        _ = TokenAlertDetailGeneric(**stats[0])

    # Check that the returned history has a single hit
    history_resp = get_token_history(token_info, version=version)

    token_history = WebBugTokenHistory(**history_resp)

    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "HTTP"
    if version.live:
        # TODO: Remove once v3 is live
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    assert token_hit.useragent == useragent


@pytest.mark.parametrize(
    "location, referrer, version",
    [
        ("http://test.com/testloc", "http://test.com/testref", v2),
        ("http://test.com/testloc", "http://test.com/testref", v3),
        ("http://test.com/testloc2", "about:blank", v2),
        ("http://test.com/testloc2", "about:blank", v3),
    ],
)
def test_cloned_web_token(
    location: str,
    referrer: str,
    version: Union[V2, V3],
    webhook_receiver,
    runv2,
    runv3,
) -> None:
    """
    Tests: cloned_web
    """
    run_or_skip(version, runv2=runv2, runv3=runv3)
    memo = "Test stuff break stuff test stuff sometimes build stuff"
    # Create a cloned web token request
    token_request = ClonedWebTokenRequest(
        webhook_url=webhook_receiver,
        memo=memo,
        clonedsite="http://www.test.com",
    )
    resp = create_token(token_request, version=version)

    token_info = ClonedWebTokenResponse(**resp)
    # Trigger the token
    _ = trigger_http_token(
        token_info=token_info,
        version=version,
        params={"l": location, "r": referrer},
    )
    # _ = requests.get(token_info.token_url, params=)

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats is not None:
        # Check that what was sent to the webhook is consistent.
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    # Check that the returned history has a single hit

    history_resp = get_token_history(token_info, version=version)

    token_history = ClonedWebTokenHistory(**history_resp)

    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.referer == referrer
    assert token_hit.location == location
    if version.live:
        # Todo: remove when v3 runs as a live server.
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    else:
        assert token_hit.geo_info.ip == "127.0.0.1"


@pytest.mark.parametrize(
    "target,version",
    [
        ("https://www.youtube.com", v3),
        ("https://www.youtube.com", v2),
        # ("google.com") # without http[s]://
    ],
)
def test_fast_redirect_token(target: str, version, runv2, runv3) -> None:
    """
    Tests: fast_redirect
    """
    run_or_skip(version, runv2=runv2, runv3=runv3)
    # Create a fast redirect token request
    token_request = FastRedirectTokenRequest(
        webhook_url=HttpUrl(url="https://hooks.slack.com/test", scheme="https"),
        memo=Memo("Test stuff break stuff test stuff sometimes build stuff"),
        redirect_url=target,
    )
    resp = create_token(token_request, version=version)

    token_info = FastRedirectTokenResponse(**resp)

    # Trigger the token
    trigger_resp = trigger_http_token(
        token_info=token_info, version=version, allow_redirects=True
    )

    # Make sure the redirect worked:
    assert trigger_resp.url == target

    # Check that the returned history has a single hit
    history_resp = get_token_history(token_info, version=version)
    token_history = FastRedirectTokenHistory(**history_resp)

    assert len(token_history.hits) == 1


@pytest.mark.parametrize(
    "target, location, referrer, version",
    [
        (
            "https://www.youtube.com",
            "http://test.com/testloc",
            "http://test.com/testref",
            v3,
        ),
        (
            "http://www.youtube.com",
            "http://test.com/testloc",
            "http://test.com/testref",
            v2,
        ),
        (
            "https://www.youtube.com",
            "http://test.com/testloc",
            "http://test.com/testref",
            v2,
        ),
        # https://github.com/thinkst/canarytokens/issues/122
        # in future add one without http[s]:// (currently broken)
    ],
)
def test_slow_redirect_token(
    target: str, location: str, referrer: str, version, webhook_receiver, runv2, runv3
) -> None:
    """
    Tests: slow_redirect
    """
    run_or_skip(version, runv2=runv2, runv3=runv3)
    memo = "Test stuff break stuff test stuff sometimes build stuff"
    # Create a slow redirect token request
    token_request = SlowRedirectTokenRequest(
        webhook_url=webhook_receiver,
        memo=memo,
        redirect_url=target,
    )
    resp = create_token(token_request, version=version)

    token_info = SlowRedirectTokenResponse(**resp)

    # Trigger the token
    trigger_resp = trigger_http_token(
        token_info=token_info, version=version, params={"l": location, "r": referrer}
    )

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats is not None:
        # Check that what was sent to the webhook is consistent.
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    key = re.findall(r"'key='\+encodeURIComponent\('(\d+.\d+)", trigger_resp.text)
    assert len(key) == 1

    data_1 = {
        "key": key,
        "canarytoken": token_info.token,
        "name": "Browser",
        "enabled": "1",
        "installed": "1",
        "browser": "Chrome",
        "version": "99.0.4844.84",
        "mimetypes": "",
        "language": "en-US",
        "platform": "MacIntel",
        "vendor": "Google Inc.",
        "os": "Macintosh",
    }
    data_2 = {
        "key": key,
        "canarytoken": token_info.token,
        "name": "Javascript",
        "version": "",
        "enabled": "1",
        "installed": "1",
    }
    # Make sure the redirect is in the doc
    assert target in trigger_resp.text

    # Send the POST the JS *would* have sent
    requests.post(trigger_resp.url, data_1)
    requests.post(trigger_resp.url, data_2)

    # Check that the returned history has a single hit
    history_resp = get_token_history(token_info, version=version)

    token_history = SlowRedirectTokenHistory(**history_resp)

    assert len(token_history.hits) == 1
    assert token_history.hits[0].additional_info.browser.vendor == ["Google Inc."]
    #


@pytest.mark.parametrize("version", [v3, v2])
def test_broken_webhook_on_token_creation(version, runv2, runv3):
    token_request = ClonedWebTokenRequest(
        webhook_url=HttpUrl(url="https://something.com/nothing", scheme="https"),
        memo=Memo("Test stuff break stuff test stuff sometimes build stuff"),
        clonedsite="test.com",
    )
    run_or_skip(version, runv2=runv2, runv3=runv3)
    if isinstance(version, V2):
        with pytest.raises(CanaryTokenCreationError):
            _ = create_token.__wrapped__(token_request, version=version)
    elif isinstance(version, V3):  # pragma: no cover
        # V3 will use http codes to indicate a failed token creation
        with pytest.raises(requests.exceptions.HTTPError):
            _ = create_token.__wrapped__(token_request, version=version)
    else:
        assert False, f"Unsupported version {version}"
