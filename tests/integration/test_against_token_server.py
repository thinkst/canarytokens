import re
from functools import partial
from smtplib import SMTP

from frontend.app import ROOT_API_ENDPOINT
import pytest
import requests
from pydantic import HttpUrl
from requests import HTTPError

from canarytokens.models import (
    AlertStatus,
    CanarydropSettingsTypes,
    ClonedWebTokenHistory,
    ClonedWebTokenRequest,
    ClonedWebTokenResponse,
    DNSTokenHistory,
    DNSTokenRequest,
    DNSTokenResponse,
    DownloadFmtTypes,
    DownloadIncidentListJsonRequest,
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
    WebBugTokenHistory,
    WebBugTokenRequest,
    WebBugTokenResponse,
    WindowsDirectoryTokenHistory,
    WindowsDirectoryTokenRequest,
    WindowsDirectoryTokenResponse,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric
from canarytokens.settings import SwitchboardSettings
from tests.utils import (
    clear_stats_on_webhook,
    create_token,
    delete_token,
    get_stats_from_webhook,
    get_token_history,
    log_4_shell_fire_token,
    plain_fire_token,
    slack_webhook_test,
    trigger_http_token,
    windows_directory_fire_token,
    server_config,
)


def test_delete_token():
    token_request = DNSTokenRequest(
        webhook_url=slack_webhook_test,
        email="test@test.com",
        memo="We are v3",
    )
    resp = create_token(token_request)

    # Check dns token has correct attributes
    token_info = DNSTokenResponse(**resp)

    # Trigger it once
    _ = plain_fire_token(token_info)

    # Check that we can query the token's history
    resp = get_token_history(token_info=token_info)
    _ = DNSTokenHistory(**resp)

    resp = delete_token(token_info.token, token_info.auth_token)
    assert resp.get("message") == "success"

    token_history_request = DownloadIncidentListJsonRequest(
        token=token_info.token,
        # TODO: auth vs. auth_token choose one at least at the object level
        auth=token_info.auth_token,
        fmt=DownloadFmtTypes.INCIDENTLISTJSON,
    )
    resp = requests.get(
        url=f"{server_config.server_url}/download", params=token_history_request
    )

    assert resp.status_code == 403


@pytest.mark.parametrize(
    "token_request_type, token_response_type, token_history_type, token_trigger",
    [
        (DNSTokenRequest, DNSTokenResponse, DNSTokenHistory, plain_fire_token),
        (
            WindowsDirectoryTokenRequest,
            WindowsDirectoryTokenResponse,
            WindowsDirectoryTokenHistory,
            partial(windows_directory_fire_token, domain="username.hostname.domain"),
        ),
        (
            Log4ShellTokenRequest,
            Log4ShellTokenResponse,
            Log4ShellTokenHistory,
            partial(log_4_shell_fire_token, retrieved_hostname="somehostname.local"),
        ),
    ],
)
def test_dns_triggered_tokens(
    webhook_receiver,
    token_request_type,
    token_response_type,
    token_history_type,
    token_trigger,
):
    """
    Tests all tokens that are triggered via the DNS channel. It's a fully `parametrize`'d
    test and covers just the basics.

    Currently runs: dns, log4shell, windows_directory

    If more specialized tests are needed for a particular token type then
    add those as a separate test. That is advisable over making this complex test even more
    complex.
    """

    # Create a DNS token request
    memo = "Test stuff break stuff test stuff sometimes build stuff"

    token_request = token_request_type(
        webhook_url=webhook_receiver,
        memo=memo,
    )
    resp = create_token(token_request)

    # Check dns token has correct attributes
    token_info = token_response_type(**resp)
    # assert dns_token_info.webhook_url == token_request.webhook_url
    assert token_info.hostname.split(".")[0] == token_info.token

    clear_stats_on_webhook(webhook_receiver, token=token_info.token)
    # Trigger DNS token
    _ = token_trigger(token_info)

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats is not None:
        # Check that what was sent to the webhook is consistent.
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])
    # Check that the returned history has a single hit.
    resp = get_token_history(token_info=token_info)

    token_history = token_history_type(**resp)
    # TODO: what other fields do we want to assert on.
    #       note: making them TokenHistory have stronger validators is
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
    "hostname_to_retrieve",
    [
        "testhost.name.com",
    ],
)
def test_log_4_shell_token(hostname_to_retrieve, webhook_receiver):
    """Tests the Log4Shell token. Creates a token with `webhook_receiver` as
    the output channel. Triggers the token with with `computer_name` as `hostname_to_retrieve`
    and checks that it is correctly recovered in the `src_data`.

    Args:
        hostname_to_retrieve (str): computer_name that we want to recover based on how it's added to the token.
        webhook_receiver (str): A webhook receiver yto
    """

    # Create a DNS token request
    memo = "Test stuff break stuff test stuff sometimes build stuff"

    dns_request = Log4ShellTokenRequest(
        webhook_url=webhook_receiver,
        memo=memo,
    )

    resp = create_token(dns_request)
    # Check dns token has correct attributes
    token_info = Log4ShellTokenResponse(**resp)
    assert token_info.hostname.split(".")[0] == token_info.token

    # Clear the webhook stats
    clear_stats_on_webhook(webhook_receiver, token=token_info.token)
    # Trigger the token
    hostname_to_retrieve = hostname_to_retrieve.strip()
    _ = log_4_shell_fire_token(token_info, retrieved_hostname=hostname_to_retrieve)

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
    resp = get_token_history(token_info=token_info)
    token_history = Log4ShellTokenHistory(**resp)
    assert (
        token_history.hits[0].src_data["log4_shell_computer_name"].lower()
        == hostname_to_retrieve.lower()
    )


@pytest.mark.parametrize(
    "memo",
    [
        "V3 email test run",
    ],
)
def test_unique_email_token(
    memo: str,
    webhook_receiver: str,
    settings: SwitchboardSettings,
):
    """
    Tests unique email token. Creates a token with random memo and triggers
    it by sending an email. Checks that the token history is consistent and the revovered
    details are correct.
    """

    # Create SMTP token
    smtp_token_request = SMTPTokenRequest(
        webhook_url=webhook_receiver,
        memo=memo,
    )
    #
    resp = create_token(smtp_token_request)
    unique_email = resp.pop("unique_email", None)
    smtp_token_response = SMTPTokenResponse(**resp, unique_email=unique_email)

    clear_stats_on_webhook(webhook_receiver, token=smtp_token_response.token)
    # Trigger SMTP token
    sender = SMTP(
        host=server_config.canarytokens_domain,
        port=25 if server_config.live else int(settings.CHANNEL_SMTP_PORT),
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
    with open("data/canary_image.png", mode="rb") as fp:
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
    resp = get_token_history(token_info=smtp_token_response)

    token_history = SMTPTokenHistory(**resp)
    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "SMTP"  # TODO: input channel should be an enum
    if server_config.live:
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    else:
        assert token_hit.geo_info.ip == "127.0.0.1"


@pytest.mark.parametrize(
    "method",
    ["GET", "POST", "OPTIONS"],
)
def test_web_bug_token(method: str, webhook_receiver) -> None:
    """
    Tests: web_bug_token
    """

    memo = "Testing Web Bug from V3 test suite "
    useragent = "python4 from the future"
    # Create a cloned web token request
    token_request = WebBugTokenRequest(
        webhook_url=webhook_receiver,
        # email = email,
        memo=memo,
    )
    resp = create_token(token_request)

    token_info = WebBugTokenResponse(**resp)

    assert not token_info.token_url.lower().endswith((".png", ".gif", ".jpg", ".jpeg"))

    # Trigger the token
    trigger_http_token(
        token_info=token_info,
        headers={"User-Agent": useragent},
        method=method,
    )

    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)

    if stats is not None:
        # Check that what was sent to the webhook is consistent.
        assert len(stats) == 1
        assert stats[0]["memo"] == memo
        assert stats[0]["additional_data"]["useragent"] == useragent
        _ = TokenAlertDetailGeneric(**stats[0])

    # Check that the returned history has a single hit
    history_resp = get_token_history(token_info)

    token_history = WebBugTokenHistory(**history_resp)

    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "HTTP"
    if server_config.live:
        # TODO: Remove once v3 is live
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    assert token_hit.useragent == useragent


@pytest.mark.parametrize(
    "location, referrer",
    [
        (
            "https://example.com/sitemap123456789123523134521239172390182312369879081283123126.xml",
            "",
        ),
        ("http://test.com/testloc", "http://test.com/testref"),
        ("http://test.com/testloc2", "about:blank"),
    ],
)
def test_cloned_web_token(
    location: str,
    referrer: str,
    webhook_receiver,
) -> None:
    """
    Tests: cloned_web
    """

    memo = "Test stuff break stuff test stuff sometimes build stuff"
    # Create a cloned web token request
    token_request = ClonedWebTokenRequest(
        webhook_url=webhook_receiver,
        memo=memo,
        clonedsite="http://www.test.com",
    )
    resp = create_token(token_request)

    token_info = ClonedWebTokenResponse(**resp)
    # Trigger the token
    _ = trigger_http_token(
        token_info=token_info,
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

    history_resp = get_token_history(token_info)

    token_history = ClonedWebTokenHistory(**history_resp)

    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.referer == referrer
    assert token_hit.location == location
    if server_config.live:
        # Todo: remove when v3 runs as a live server.
        assert token_hit.geo_info.ip == requests.get("https://ipinfo.io/ip").text
    else:
        assert token_hit.geo_info.ip == "127.0.0.1"


@pytest.mark.parametrize(
    "target",
    [
        "https://www.youtube.com",
        # ("google.com") # without http[s]://
    ],
)
def test_fast_redirect_token(target: str) -> None:
    """
    Tests: fast_redirect
    """

    # Create a fast redirect token request
    token_request = FastRedirectTokenRequest(
        webhook_url=HttpUrl(url="https://slack.com/api/api.test", scheme="https"),
        memo=Memo("Test stuff break stuff test stuff sometimes build stuff"),
        redirect_url=target,
    )
    resp = create_token(token_request)

    token_info = FastRedirectTokenResponse(**resp)

    # Check token url page extension
    assert not token_info.token_url.lower().endswith((".png", ".gif", ".jpg", ".jpeg"))

    # Trigger the token
    trigger_resp = trigger_http_token(token_info=token_info, allow_redirects=True)

    # Make sure the redirect worked:
    assert trigger_resp.url == target

    # Check that the returned history has a single hit
    history_resp = get_token_history(token_info)
    token_history = FastRedirectTokenHistory(**history_resp)

    assert len(token_history.hits) == 1


@pytest.mark.parametrize(
    "target, location, referrer",
    [
        (
            "https://www.youtube.com",
            "http://test.com/testloc",
            "http://test.com/testref",
        ),
        # https://github.com/thinkst/canarytokens/issues/122
        # in future add one without http[s]:// (currently broken)
    ],
)
def test_slow_redirect_token(
    target: str, location: str, referrer: str, webhook_receiver
) -> None:
    """
    Tests: slow_redirect
    """

    memo = "Test stuff break stuff test stuff sometimes build stuff"
    # Create a slow redirect token request
    token_request = SlowRedirectTokenRequest(
        webhook_url=webhook_receiver,
        memo=memo,
        redirect_url=target,
    )
    resp = create_token(token_request)

    token_info = SlowRedirectTokenResponse(**resp)

    # Check token url page extension
    assert not token_info.token_url.lower().endswith((".png", ".gif", ".jpg", ".jpeg"))

    # Trigger the token
    trigger_resp = trigger_http_token(
        token_info=token_info, params={"l": location, "r": referrer}
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
    history_resp = get_token_history(token_info)

    token_history = SlowRedirectTokenHistory(**history_resp)

    assert len(token_history.hits) == 1
    token_hit = token_history.hits[0]
    assert token_hit.location == location
    assert token_hit.referer == referrer
    assert token_hit.additional_info.browser.vendor == ["Google Inc."]
    #


@pytest.mark.parametrize(
    "request_dict, error_code",
    [
        # malformed request
        ({"x": "y"}, "1"),
        # no memo - fails v3 validation
        # TODO: specialise validation
        ({"token_type": "dns", "email": "x@yz.com"}, "1"),
        # bad webhook
        (
            {
                "token_type": "dns",
                "memo": "test",
                "webhook_url": "https://something.com/nothing",
            },
            "3",
        ),
        # ? not sure what this is for
        # ({'token_type': 'dns', ...}, '4'),
        # invalid email - fails v3 validation
        ({"token_type": "dns", "memo": "test", "email": "not_an_email"}, "1"),
        # blocked email - skip, can't block via API
        # ({'token_type': 'dns', ...}, '6'),
    ],
)
def test_token_error_codes(request_dict: dict[str, str], error_code: str):

    error = "error"
    req_kw = "json"

    resp = requests.post(
        url=f"{server_config.server_url}/generate",
        timeout=(26, 26),
        **{req_kw: request_dict},
        headers={"Connection": "close"},
    )
    with pytest.raises(HTTPError):
        resp.raise_for_status()
    code = resp.json()[error]
    assert code == error_code


def test_ip_ignored_token_hit(webhook_receiver):
    """
    Tests that if a token is triggered from an ignored IP then the hit is marked  with the alerts_status as ignored_ip.
    """

    token_request = WebBugTokenRequest(
        webhook_url=webhook_receiver,
        memo="test",
    )
    token_data = create_token(token_request)

    ip_ignore_list = ["127.0.0.1"]
    # Set the token to ignore the localhost IP
    resp = requests.post(
        url=f"{server_config.server_url}/{ROOT_API_ENDPOINT}/settings/ip-ignore-list",
        json={
            "token": token_data["token"],
            "auth": token_data["auth_token"],
            "ip_ignore_list": ip_ignore_list,
        },
    )
    resp.raise_for_status()

    # make sure IP ignoring is enabled
    resp = requests.post(
        url=f"{server_config.server_url}/{ROOT_API_ENDPOINT}/settings",
        json={
            "token": token_data["token"],
            "auth": token_data["auth_token"],
            "setting": CanarydropSettingsTypes.IPIGNORESETTING,
            "value": "on",
        },
    )
    resp.raise_for_status()

    # check that the ignore list was set
    manage_resp = requests.get(
        url=f"{server_config.server_url}/{ROOT_API_ENDPOINT}/manage",
        params={
            "token": token_data["token"],
            "auth": token_data["auth_token"],
        },
    )
    manage_resp.raise_for_status()
    assert manage_resp.json()["canarydrop"]["alert_ignored_ips"] == ip_ignore_list

    # trigger the token
    resp = trigger_http_token(
        token_info=WebBugTokenResponse(**token_data),
    )
    resp.raise_for_status()

    # check that the hit is marked as ignored_ip
    token_history = get_token_history(token_info=WebBugTokenResponse(**token_data))
    assert token_history["hits"][0]["alert_status"] == AlertStatus.IGNORED_IP.value
