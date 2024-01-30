from collections import defaultdict
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime
from distutils.util import strtobool
from functools import wraps
from logging import Logger
from typing import Callable, Dict, Optional, Union

import dns.resolver
import pytest
import requests
from dns.resolver import LifetimeTimeout
from pydantic import EmailStr, HttpUrl, parse_obj_as

from canarytokens.exceptions import CanaryTokenCreationError
from canarytokens.models import (
    V2,
    V3,
    AdditionalInfo,
    AnyTokenHit,
    AnyTokenRequest,
    AnyTokenResponse,
    AWSKeyAdditionalInfo,
    AWSKeyTokenResponse,
    AzureIDTokenResponse,
    AzureIDAdditionalInfo,
    CustomBinaryTokenRequest,
    CustomBinaryTokenResponse,
    CustomImageTokenRequest,
    CustomImageTokenResponse,
    DNSTokenResponse,
    DownloadGetRequestModel,
    DownloadIncidentListJsonRequest,
    GeoIPBogonInfo,
    KubeconfigTokenRequest,
    Log4ShellTokenResponse,
    Memo,
    SettingsRequest,
    SMTPHeloField,
    SMTPMailField,
    SvnTokenResponse,
    TokenAlertDetails,
    TokenRequest,
    TokenTypes,
    WebBugTokenResponse,
    WindowsDirectoryTokenResponse,
)
from canarytokens.tokens import Canarytoken

log = Logger("test_utils")

# TODO: Grab from env var to test the intended deployment
if strtobool(os.getenv("LIVE", "False")):
    v2 = V2(
        canarytokens_sld="canarytokens.org",
        canarytokens_domain="canarytokens.org",
        canarytokens_dns_port=53,
        scheme="https",
        canarytokens_http_port=-1,
    )
else:
    v2 = V2(
        canarytokens_sld="frontend:8082",
        canarytokens_domain="127.0.0.1",
        canarytokens_dns_port=5354,
        canarytokens_http_port=8083,
        scheme="http",
    )
# TODO: Once we clean out the v2 testing we can refactor this.

if strtobool(os.getenv("LIVE", "False")):
    v3 = V3(
        canarytokens_sld="canarytokens.org",
        canarytokens_domain="canarytokens.org",
        canarytokens_dns_port=53,
        scheme="https",
        canarytokens_http_port=-1,
    )
else:
    v3 = V3(
        canarytokens_sld="127.0.0.1:8082",
        canarytokens_domain="127.0.0.1",
        canarytokens_dns_port=5354,
        canarytokens_http_port=8083,
        scheme="http",
    )
# This is a tmp personal slack account for testing / learning
# TODO: Make this a thinkst slack webhook.
slack_webhook_test = "https://hooks.slack.com/services/Not/valid"

# Note: Limit connections to ngrok as the max is 20 and the tokens server keeps
# a few open as well.

adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=3)
session = requests.Session()
session.mount("http://", adapter)
request_timeout = (26, 26)


def run_or_skip(version: Union[V2, V3], *, runv2, runv3) -> None:
    """Checks is a test should run."""
    if isinstance(version, V2) and not runv2:
        pytest.skip("Not running V2 tests. Use --runv2 to enable them")
    elif isinstance(version, V3) and not runv3:
        pytest.skip("Not running V3 tests. Use --runv3 to enable them")
    elif version is None:
        pytest.skip("Not running test. Bypassing!")
    else:
        return


def grab_resolver(version: Union[V2, V3]):
    # DESIGN: Hit the tokens server directly. If this is used as a monitor please add
    #        other popular name servers.
    resolver = dns.resolver.Resolver()
    resolver.nameservers = version.canarytokens_ips
    resolver.nameserver_ports = {
        ip: version.canarytokens_dns_port for ip in version.canarytokens_ips
    }
    return resolver


class ShouldBeStats(Exception):
    """This is just for test suite."""

    ...


def log_4_shell_fire_token(
    token_info: Log4ShellTokenResponse, retrieved_hostname: str, version: Union[V2, V3]
) -> str:
    """
    Triggers a log 4 shell token by making a dns query with the expected parameters as ldap lookup would do.

    Args:
        token_info (Log4ShellTokenResponse): log 4 shell token.
        retrieved_hostname (str): log 4 shell token makes a $hostname lookup and sends this by prepending it to the query.
                                `retrieved_hostname` is a surrogate for that lookup. This field has a max length of 100 as
                                the total length passed to `resolve` may be at most 253.
    """
    resolver = grab_resolver(version=version)
    resolver.resolve(
        token_info.token_with_usage_info.format(hostname=retrieved_hostname), "A"
    )
    return retrieved_hostname


def windows_directory_fire_token(
    token_info: WindowsDirectoryTokenResponse, domain: str, version: Union[V2, V3]
) -> str:
    """
    Triggers a Windows directory token by making a dns query with the expected parameters as Windows would produce.
    The parameterized test `test_against_token_server.py::test_dns_triggered_tokens` can't provide token-specific info,
    so we cater for that case by regenerating the full URL here.

    Args:
        token_info (WindowsDirectoryTokenResponse): the token.
        retrieved_url (str): the ini file in the windows directory token gets a url which gives us info via the DNS lookup
                             if run locally the get would fail, so this emulates the DNS fire we would receive.

    """
    if token_info.token in domain:
        target = domain
    else:
        target = f"{domain}.ini.{token_info.token}.{token_info.hostname}"
    resolver = grab_resolver(version=version)
    resolver.resolve(target, "A")
    return target


def retry_on_failure(
    retry_when_raised: tuple[Exception, ...],
    retry_intervals: tuple[float, ...] = (3.0, 3.0, 5.0, 5.0),
) -> Callable:
    """Decorator to add retries to functions that depend on external systems.

    Args:
        retry_when_raised (Tuple[Exception]): If any of the Exceptions in this tuple are raised the call will be retried
        retry_intervals (List[int]): List of seconds to wait before retrying. Defaults (3., 3., 3.)
    Returns:
        Callable: Returns the wrapped function.
    """

    def inner(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):  # type: ignore
            most_recent_error = None
            for interval in retry_intervals:
                try:
                    res = f(*args, **kwargs)
                except retry_when_raised as e:  # pragma: no cover
                    most_recent_error = e
                    time.sleep(interval)  # pragma: no cover
                    continue  # pragma: no cover
                else:
                    return res
            raise Exception(
                f"Retrying {f} failed after {len(retry_intervals)} attempts and {sum(retry_intervals)}s"
                f"; Most recent error: {most_recent_error}"
            )  # pragma: no cover

        return wrapper

    return inner


@retry_on_failure(retry_when_raised=(LifetimeTimeout,))
def plain_fire_token(
    token_info: Union[
        DNSTokenResponse,
        WindowsDirectoryTokenResponse,
        CustomBinaryTokenResponse,
        SvnTokenResponse,
    ],
    version: Union[V2, V3],
) -> None:
    """Triggers a token via the dns channel.

    Args:
        token_info (Union[DNSTokenResponse, WindowsDirectoryTokenResponse, CustomBinaryTokenResponse, SvnTokenResponse]): Token info in a concrete class. This is the token that gets triggered.
    """
    resolver = grab_resolver(version=version)
    # if "127.0.0.1" in token_info.hostname:
    #     hostname,_,_ = token_info.hostname.partition(":")
    #     hostname = f"{hostname}:8083"
    # else:
    #     hostname = token_info.hostname
    _ = resolver.resolve(token_info.hostname, "A")


def aws_token_fire(token_info: AWSKeyTokenResponse, version: Union[V2, V3]) -> None:
    """Triggers an AWS token via the HTTP channel. This mimics the 'ProcessUserAPITokenLogs'
    lambda POST.

    Args:
        token_info (AWSTokenResponse): This is the token that gets triggered.
    """
    if version.live:
        url = token_info.token_url
    else:
        # Need to hit Switchboard directly.
        http_url = parse_obj_as(HttpUrl, token_info.token_url)
        http_url.port = version.canarytokens_http_port
        url = f"{http_url.scheme}://{http_url.host}:{http_url.port}{http_url.path}"
    data = {
        "ip": "128.2.4.98",
        "user_agent": "Mozilla/5.0, AppleWebKit/537.36, Chrome/80.0.3987.132",
    }
    data["eventName"] = "GetCallerIdentity"

    data = urllib.parse.urlencode(data).encode("utf8")

    req = urllib.request.Request(url, data)
    _ = urllib.request.urlopen(req)


def azure_token_fire(
    token_info: AzureIDTokenResponse, data: dict, version: Union[V2, V3]
) -> None:
    """Triggers an Azure token via the HTTP channel.
    This mimics the POST we receive.

    Args:
        token_info (AzureIDTokenResponse): This is the token that gets triggered.
        data (dict): the data that would be passed as the body
    """
    if version.live:
        url = token_info.token_url
    else:
        # Need to hit Switchboard directly.
        http_url = parse_obj_as(HttpUrl, token_info.token_url)
        http_url.port = version.canarytokens_http_port
        url = f"{http_url.scheme}://{http_url.host}:{http_url.port}{http_url.path}"

    resp = requests.post(url, json=data)
    resp.raise_for_status()


@retry_on_failure(retry_when_raised=(requests.exceptions.HTTPError,))
def get_token_history(
    token_info: Union[
        Log4ShellTokenResponse,
        DNSTokenResponse,
        WindowsDirectoryTokenResponse,
        WebBugTokenResponse,
        CustomBinaryTokenResponse,
        CustomImageTokenResponse,
    ],
    version: Union[V2, V3],
    expected_len: int = 1,
    fmt="incidentlist_json",
) -> Dict[str, str]:
    token_history_request = DownloadIncidentListJsonRequest(
        token=token_info.token,
        # TODO: auth vs. auth_token choose one at least at the object level
        auth=token_info.auth_token,
        fmt=fmt,
    )
    resp = session.get(
        url=f"{version.server_url}/download",
        params=token_history_request.dict(),
    )
    resp.raise_for_status()
    session.close()
    data = resp.json()
    data["token_type"] = data.get("token_type", None) or token_info.token_type
    if isinstance(data.get("hits"), list) and len(data.get("hits")) < expected_len:
        raise requests.exceptions.HTTPError("No history found")
    return data


@retry_on_failure(retry_when_raised=(requests.exceptions.HTTPError,))
def download_token_artifact(
    token_info: AnyTokenResponse,
    version: Union[V2, V3],
    fmt="incidentlist_json",
) -> Dict[str, str]:
    token_history_request = DownloadGetRequestModel(
        token=token_info.token,
        # TODO: auth vs. auth_token choose one at least at the object level
        auth=token_info.auth_token,
        fmt=fmt,
    )
    resp = session.get(
        url=f"{version.server_url}/download",
        params=token_history_request.dict(),
    )
    resp.raise_for_status()
    session.close()
    return resp.content


@retry_on_failure(retry_when_raised=(requests.exceptions.HTTPError, ShouldBeStats))
def get_stats_from_webhook(webhook_receiver: str, token: str):
    if "slack" in webhook_receiver:
        # slack webhooks don't give us introspection. Or can we? TODO: take a look.
        return  # pragma: no cover
    stats = defaultdict(list)
    uuid = webhook_receiver.split("/")[-1]
    time.sleep(1.0)
    resp = session.get(
        f"https://webhook.site/token/{uuid}/requests",
        timeout=request_timeout,
        headers={"Connection": "close"},
    )
    resp.raise_for_status()
    webhook_data = resp.json()
    resp.close()
    session.close()
    if not webhook_data["total"] > 0:
        raise ShouldBeStats("we'll wait a bit for webhooks to get hit")
    for req in webhook_data["data"]:
        data = json.loads(req["content"])
        # HACK: we can do better but that would be an API change:
        if "http://example.com/test/url/for/webhook" != data.get("manage_url", None):
            token_and_auth = data["manage_url"].split("/")[-1]
            token = token_and_auth.split("&")[0].split("=")[1]
            stats[token].append(data)
    return stats[token]


@retry_on_failure(retry_when_raised=(requests.exceptions.HTTPError,))
def clear_stats_on_webhook(webhook_receiver: str, token: str):
    """remove all requests associated with a specific token on this webhook"""
    if "slack" in webhook_receiver:
        # slack webhooks don't give us introspection. or TODO: check how to!
        return  # pragma: no cover
    webhook_uuid = webhook_receiver.split("/")[-1]
    # get all the requests
    resp = session.get(
        f"https://webhook.site/token/{webhook_uuid}/requests",
        timeout=request_timeout,
        headers={"Connection": "close"},
    )
    resp.raise_for_status()
    webhook_data = resp.json()
    resp.close()
    session.close()
    for req in webhook_data["data"]:
        delete_req = False
        data = json.loads(req["content"])
        token_uuid = req["uuid"]
        # HACK: we can do better but that would be an API change:
        if "http://example.com/test/url/for/webhook" == data.get("manage_url", None):
            delete_req = True
        else:
            token_and_auth = data["manage_url"].split("/")[-1]
            current_token = token_and_auth.split("&")[0].split("=")[1]
            if current_token == token:
                delete_req = True
        if delete_req:
            resp = session.delete(
                f"https://webhook.site/token/{webhook_uuid}/request/{token_uuid}",
                timeout=request_timeout,
                headers={"Connection": "close"},
            )
            resp.raise_for_status()
            resp.close()
            session.close()


@retry_on_failure(retry_when_raised=(requests.exceptions.HTTPError,))
def set_token_settings(setting: SettingsRequest, version: Union[V2, V3]):
    generate_url = f"{version.server_url}/settings"
    kwargs = {}
    if isinstance(version, V2):
        kwargs["data"] = setting.dict()
    elif isinstance(version, V3):
        kwargs["json"] = setting.dict()

    resp = session.post(
        url=generate_url,
        timeout=request_timeout,
        **kwargs,
        headers={"Connection": "close"},
    )
    resp.raise_for_status()
    data = resp.json()
    resp.close()
    session.close()
    return data


@retry_on_failure(
    retry_when_raised=(requests.exceptions.HTTPError, CanaryTokenCreationError)
)
def create_token(token_request: TokenRequest, version: Union[V2, V3]):
    generate_url = f"{version.server_url}/generate"
    kwargs = {}
    timeout = request_timeout
    if isinstance(version, V2):
        kwargs["data"] = token_request.to_dict(version=version)
    elif isinstance(version, V3):
        if isinstance(
            token_request, (CustomImageTokenRequest, CustomBinaryTokenRequest)
        ):
            kwargs["data"] = token_request.to_dict(version=version)
        elif isinstance(token_request, KubeconfigTokenRequest):
            timeout = (60, 60)  # the devcontainer is *slow*
            kwargs["json"] = token_request.to_dict(version=version)
        else:
            kwargs["json"] = token_request.to_dict(version=version)
    else:
        raise ValueError(f"Version not supported: {version}")

    if isinstance(token_request, CustomImageTokenRequest):
        kwargs["files"] = {
            "web_image": (
                token_request.web_image.filename,
                token_request.web_image.file,
                token_request.web_image.content_type,
            )
        }
    if isinstance(token_request, CustomBinaryTokenRequest):
        kwargs["files"] = {
            "signed_exe": (
                token_request.signed_exe.filename,
                token_request.signed_exe.file,
                token_request.signed_exe.content_type,
            )
        }

    resp = session.post(
        url=generate_url,
        timeout=timeout,
        **kwargs,
        headers={"Connection": "close"},
    )
    if resp.status_code >= 400:
        log.error(
            f"Token creation error: \n\t{token_request=}\n\t{resp.status_code=}; {resp.json()=}"
        )
    resp.raise_for_status()
    data = resp.json()
    resp.close()
    session.close()
    # TODO / DESIGN: The webhook receiver sometimes chokes due to ngrok rate limit 429 error.
    #                retry for now. +1 for a webhook receiver as a docker service.
    if (
        isinstance(version, V2) and data["Error"] == 3
    ):  # webhook failed not the servers fault
        raise CanaryTokenCreationError("Webhook failed to validate")  # pragma: no cover

    return data


def make_token_alert_detail(
    channel: Optional[str] = None,
    token_type: Optional[TokenTypes] = None,
    memo: Optional[Memo] = None,
):
    return TokenAlertDetails(
        token=Canarytoken().value(),
        channel=channel or "DNS",
        token_type=token_type or TokenTypes.DNS,
        memo=memo or Memo("Fake alert token details"),
        additional_data={},
        time=datetime.utcnow(),
        manage_url="https://this.is/manage/token",
        src_ip="127.0.0.1",
    )


def get_token_request(token_request_type: AnyTokenRequest) -> AnyTokenRequest:
    return token_request_type(
        email="test@test.com",
        webhook_url="https://slack.com/api/api.test",
        memo="test stuff break stuff fix stuff test stuff",
        redirect_url="https://youtube.com",
        clonedsite="https://test.com",
        cmd_process="klist.exe",
        azure_id_cert_file_name="test.pem",
        expected_referrer="testreferrer.com",
    )


def get_basic_hit(token_type: TokenTypes) -> AnyTokenHit:
    if token_type == TokenTypes.WIREGUARD:
        src_data = {
            "src_port": 8833,
            "server_public_key": "serverpublickey",
            "client_public_key": "clientpublickey",
            "session_index": "12345678",
        }
    else:
        src_data = {}
    if token_type == TokenTypes.AWS_KEYS:
        additional_info = AWSKeyAdditionalInfo(
            aws_key_log_data={
                "safety_net": ["True"],
                "last_used": ["2022-07-29T05:48:00+00:00"],
            }
        )
    elif token_type == TokenTypes.AZURE_ID:
        additional_info = AzureIDAdditionalInfo(
            coordinates={"latitude": ["-25.73"], "longitude": ["28.21"]},
            azure_id_log_data={
                "Date": ["2023-04-03T15:40:13.785374Z"],
                "Authentication": [
                    "\nAzure AD App Authentication Library: Family: MSAL Library: MSAL.Python 1.20.0 Platform: Python"
                ],
            },
            location={
                "city": ["Pretoria"],
                "state": ["Gauteng"],
                "countryOrRegion": ["ZA"],
            },
            microsoft_azure={
                "App ID": ["some-app-id"],
                "Resource": ["Windows Azure Service Management API"],
                "Cert ID": ["some-cert-id"],
            },
        )
    else:
        additional_info = AdditionalInfo()
    generic_hit = dict(
        token_type=token_type,
        time_of_hit=111,
        src_ip="127.0.0.1",
        is_tor_relay=False,
        input_channel="HTTP",
        referer="http://test.com",
        location="http://test.com",
        useragent="mr anderson",
        src_data=src_data,
        additional_info=additional_info,
        geo_info=GeoIPBogonInfo(ip="127.0.0.1", bogon=True),
        mail=SMTPMailField(
            attachments=[],
            recipients=[],
            headers=[],
            sender=EmailStr("test@test.com"),
            links=[],
            helo=SMTPHeloField(client_name="test", client_ip="127.0.0.1"),
        ),
    )
    return parse_obj_as(AnyTokenHit, generic_hit)


def trigger_http_token(
    token_info: AnyTokenResponse,
    version: Union[V2, V3],
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    method: Optional[str] = "GET",
    **kwargs: dict,
) -> requests.Response:
    """Triggers a token by making a http GET. Uses version to
    determine the port as in some cases the service is not fronted by
    nginx.

    Args:
        token_info (AnyTokenResponse): _description_
        version (Union[V2, V3]): _description_

    Returns:
        requests.Response: _description_
    """
    if version.live:
        token_url: HttpUrl = token_info.token_url
    else:
        turl: HttpUrl = token_info.token_url
        token_url = f"{turl.scheme}://{version.canarytokens_domain}:8083{turl.path}"

    _method_func = getattr(requests, method.lower())
    return _method_func(
        token_url, headers=headers, params=params, timeout=(3, 3), **kwargs
    )


def trigger_canarytokens_awsid(server: str, port: int, canarytoken: Canarytoken):
    """Perform the triggering process exactly as done in the ProcessUserAPITokensLogs lambda."""

    agent = "Boto3/1.20.46 Python/3.9.10 Darwin/21.4.0 Botocore/1.23.46"
    ip = "1.2.3.4"
    target = f"{server}:{port}"
    token = f"{canarytoken.value()}"
    url = f"http://{target}/{token}"
    data_dict = {"ip": ip, "user_agent": agent, "eventName": "GetCallerIdentity"}

    data = urllib.parse.urlencode(data_dict).encode("utf8")
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)

    print("AWS Access-key was used from IP {p!r}".format(p=ip))
    print("Looking up {u} to trigger alert!".format(u=url))
    print("Response Code: {r}".format(r=response.getcode()))
    print("Response Info: {r}".format(r=response.info()))
