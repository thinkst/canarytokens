import inspect
from datetime import datetime

import pytest
from pydantic import HttpUrl, ValidationError, parse_obj_as

from canarytokens import models
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import (
    V2,
    V3,
    AdditionalInfo,
    AnyTokenHistory,
    AnyTokenHit,
    AnyTokenRequest,
    AnyTokenResponse,
    AWSKeyTokenHit,
    ClonedWebTokenHistory,
    DNSTokenRequest,
    DownloadContentTypes,
    DownloadMSWordResponse,
    GeoIPBogonInfo,
    Log4ShellTokenHistory,
    Log4ShellTokenHit,
    Log4ShellTokenResponse,
    SlowRedirectTokenHistory,
    SlowRedirectTokenHit,
    SMTPHeloField,
    SMTPMailField,
    SMTPTokenHistory,
    SMTPTokenHit,
    TokenAlertDetailGeneric,
    TokenRequest,
    TokenTypes,
    WebBugTokenHistory,
    WebBugTokenHit,
    json_safe_dict,
)
from canarytokens.tokens import Canarytoken
from tests.utils import v2, v3


@pytest.mark.parametrize(
    "email,webhook_url, expected_exception",
    [
        ("not_an_email", "https://vailid.hook.com/test", ValidationError),
        ("valid.email@gmail.com", "not_valid_webhook", ValidationError),
        (None, None, ValidationError),
    ],
)
def test_token_request_without_webhook_or_email(email, webhook_url, expected_exception):
    with pytest.raises(expected_exception=expected_exception):
        _ = TokenRequest(
            token_type=TokenTypes.DNS,
            email=email,
            webhook_url=webhook_url,
            memo="somehting",
        )


@pytest.mark.parametrize("token_type,_type", [(TokenTypes.DNS, DNSTokenRequest)])
def test_token_request(token_type, _type):
    data = {
        "token_type": token_type,
        "email": None,
        "webhook_url": "https://slack.com/api/api.test",
        "memo": "We are v3",
    }
    _ = _type(**data)


@pytest.mark.parametrize(
    "version",
    [
        v2,
        v3,
        None,
    ],
)
def test_token_request_version_based_dict_call(version):
    tr = DNSTokenRequest(
        token_type=TokenTypes.DNS,
        webhook_url="https://hooks.test.com/test",
        memo="test",
    )
    if isinstance(version, V2):
        assert "webhook" in tr.to_dict(version=version)
    if isinstance(version, V3):
        assert "webhook_url" in tr.to_dict(version=version)
    if version is None:
        with pytest.raises(NotImplementedError):
            tr.to_dict(version=version)


@pytest.mark.parametrize(
    "token_type_key, token_type_value",
    [(o, o.lower()) for o in TokenTypes.__members__.keys()],
)
def test_token_types(token_type_key, token_type_value):
    assert str(TokenTypes(token_type_value)) == token_type_value
    assert (
        str(getattr(TokenTypes(token_type_value), token_type_key)) == token_type_value
    )


def test_alert_details():
    details = {
        "manage_url": "http://honeypdfs.com/manage?token=tm4uljrnw44z6z9ktev848wru&auth=94edd9b20fa7859de64fb30d456ad7a3",
        "memo": "0",
        "additional_data": {
            "src_ip": "34.242.239.31",
            "mail": {
                "sender": "test@test.com",
                "links": [],
                "recipients": ["<tm4uljrnw44z6z9ktev848wru@honeypdfs.net>"],
                "headers": [],
                "helo": {"client_name": "[172.21.0.3]", "client_ip": "34.242.239.31"},
                "attachments": [],
            },
        },
        "channel": "SMTP",
        "time": "2022-04-08 12:17:53 (UTC)",
        "token_type": TokenTypes.SMTP,
        "src_ip": "127.0.0.1",
        "token": "tm4uljrnw44z6z9ktev848wru",
    }
    TokenAlertDetailGeneric(**details)


@pytest.mark.parametrize(
    "memo,canarytoken,token_type,token_hist",
    [
        ("sss", Canarytoken(), TokenTypes.LOG4SHELL, Log4ShellTokenHistory(hits=[])),
        ("sss", Canarytoken(), TokenTypes.SMTP, SMTPTokenHistory(hits=[])),
        ("sss", Canarytoken(), TokenTypes.CLONEDSITE, ClonedWebTokenHistory(hits=[])),
        (
            "sss",
            Canarytoken(),
            TokenTypes.WEB,
            WebBugTokenHistory(token_type=TokenTypes.WEB, hits=[]),
        ),
        (
            "sss",
            Canarytoken(),
            TokenTypes.SLOW_REDIRECT,
            SlowRedirectTokenHistory(token_type=TokenTypes.SLOW_REDIRECT, hits=[]),
        ),
    ],
)
def test_canarydrop_model(memo, canarytoken, token_type, token_hist):
    instance = Canarydrop(
        generate=True,
        canarytoken=canarytoken,
        triggered_details=token_hist.dict(),
        type=token_type,
        memo=memo,
        redirect_url="https://youtube.com",
    )
    assert isinstance(instance.created_at, datetime)
    assert len(instance.auth) == 32
    assert isinstance(instance.triggered_details, type(token_hist))


def test_canarydrop_model_on_details():
    data = {
        "generate": True,
        "canarytoken": Canarytoken(),
        "memo": "Test stuff break stuff test stuff sometimes build stuff",
        "created_at": datetime(2022, 4, 21, 6, 10, 13),
        "triggered_details": None,
        "auth": "3bd9dff698b1b6be36b803632b444ea7",
        "type": TokenTypes.CLONEDSITE,
        "alert_email_enabled": True,
        "alert_email_recipient": None,
        "alert_sms_enabled": False,
        "alert_sms_recipient": None,
        "alert_webhook_enabled": True,
        "alert_webhook_url": HttpUrl(
            "http://0cdc-165-73-122-152.ngrok.io/alert",
            scheme="http",
            host="0cdc-165-73-122-152.ngrok.io",
            tld="io",
            host_type="domain",
            port="80",
            path="/alert",
        ),
    }
    Canarydrop(**data)


@pytest.mark.parametrize(
    "token_types, drop_types",
    [
        (sorted([o for o in TokenTypes]), sorted([o for o in TokenTypes])),
    ],
)
def test_create_canarydrop(token_types, drop_types):
    for tt, td in zip(token_types, drop_types):
        data = {
            "generate": True,
            "triggered_details": {"token_type": tt, "hits": []},
            "memo": "memo",
            "created_at": "2022-04-12T12:40:36",
            "auth": "0283681fd4fd0e0e47a1989ccfec6b14",
            "type": td,
            # 'user': User(name='anonymous', email=None),
            "alert_email_enabled": "False",
            "alert_email_recipient": "email@test.com",
            "alert_sms_enabled": "False",
            "alert_webhook_enabled": "False",
            "canarytoken": Canarytoken(),
        }
        if tt in [TokenTypes.SLOW_REDIRECT, TokenTypes.FAST_REDIRECT]:
            data["redirect_url"] = "https://youtube.com"

        cd = Canarydrop(**data)
        assert cd.triggered_details.token_type == cd.type

    for tt, td in zip(token_types[1:] + [token_types[0]], drop_types):
        data = {
            "generate": True,
            "triggered_details": {"token_type": tt, "hits": []},
            "memo": "memo",
            "created_at": "2022-04-12T12:40:36",
            "auth": "0283681fd4fd0e0e47a1989ccfec6b14",
            "type": td,
            # 'user': User(name='anonymous', email=None),
            "alert_email_enabled": "False",
            "alert_email_recipient": "email@test.com",
            "alert_sms_enabled": "False",
            "alert_webhook_enabled": "False",
            "canarytoken": Canarytoken(),
        }
        with pytest.raises(ValidationError):
            cd = Canarydrop(**data)


def test_additional_info():
    data = {
        "additional_info": {
            "MySQL Client": {
                "Locale": ["en_US"],
                "Hostname": ["thinkst-leighton.local"],
            }
        },
        "input_channel": "MYSQL",
    }
    AdditionalInfo(**data)


def test_fast_redirect_request():
    data = {
        "token_type": "fast_redirect",
        "webhook_url": "https://slack.com/api/api.test",
        "memo": "Test stuff break stuff test stuff sometimes build stuff",
        "redirect_url": "https://www.youtube.com",
    }
    from pydantic import parse_obj_as

    dd = parse_obj_as(AnyTokenRequest, data)
    assert dd.token_type == TokenTypes.FAST_REDIRECT


def test_dns_request():
    data = {
        "token_type": "dns",
        "webhook_url": "https://slack.com/api/api.test",
        "memo": "Test stuff break stuff test stuff sometimes build stuff",
    }
    from pydantic import parse_obj_as

    dd = parse_obj_as(AnyTokenRequest, data)
    assert dd.token_type == TokenTypes.DNS


def test_slow_redirect_token_hit():
    data = {
        "token_type": "slow_redirect",
        "time_of_hit": 1650634270.0,
        "src_ip": "127.0.0.1",
        "input_channel": "HTTP",
        "is_tor_relay": False,
        "referer": "http://test.com/testref",
        "location": "http://test.com/testloc",
        "useragent": "python-requests/2.27.1",
        "additional_info": {
            "Browser": {
                "l": [b"http://test.com/testloc"],
                "r": [b"http://test.com/testref"],
                "enabled": ["1"],
                "installed": [b"1"],
                "browser": [b"Chrome"],
                "version": [b"99.0.4844.84"],
                "mimetypes": [b""],
                "language": [b"en-US"],
                "platform": [b"MacIntel"],
                "vendor": [b"Google Inc."],
                "os": [b"Macintosh"],
            }
        },
    }
    sr_hit = SlowRedirectTokenHit(**data)
    assert sr_hit.additional_info.browser is not None
    ad_in = AdditionalInfo(
        **{
            "Browser": {
                "l": [b"http://test.com/testloc"],
                "r": [b"http://test.com/testref"],
                "enabled": ["1"],
                "installed": ["1"],
                "browser": [b"Chrome"],
                "version": [b"99.0.4844.84"],
                "mimetypes": [b""],
                "language": [b"en-US"],
                "platform": [b"MacIntel"],
                "vendor": [b"Google Inc."],
                "os": [b"Macintosh"],
            }
        }
    )

    assert ad_in.browser.enabled


def test_update_additional_info():
    ad_in = AdditionalInfo(
        **{
            "Browser": {
                "l": [b"http://test.com/testloc"],
                "r": [b"http://test.com/testref"],
                "enabled": ["1"],
                "installed": ["1"],
                "browser": [b"Chrome"],
                "version": [b"99.0.4844.84"],
                "mimetypes": [b""],
                "language": [b"en-US"],
                "platform": [b"MacIntel"],
                "vendor": [b"Google Inc."],
                "os": [b"Macintosh"],
            }
        }
    )
    data = ad_in.dict(exclude_unset=True)
    ad_new = AdditionalInfo(
        **{
            **data,
            **{"Javascript": {"enabled": ["1"], "version": ["1"], "installed": ["1"]}},
        }
    )
    assert ad_new.javascript.enabled == ["1"]
    assert ad_in.browser.enabled


def test_add_in():
    # class TMP(BaseModel):
    # # the ServiceInfo keys are dynamic
    # # this only works for our test
    # # Javascript: Optional[ServiceInfo]
    #     Browser: Optional[BrowserInfo]

    # class AdditionalInfo(BaseModel):
    # # the ServiceInfo keys are dynamic
    # # this only works for our test
    #     Javascript: Optional[ServiceInfo]
    #     Browser: Optional[BrowserInfo]
    #     mysql_client: Optional[dict[str, list[str]]]
    # mysql_client: Optional[dict[str, list[str]]]
    ad_in = AdditionalInfo(
        **{
            "Browser": {
                "l": [b"http://test.com/testloc"],
                "r": [b"http://test.com/testref"],
                "enabled": ["1"],
                "installed": ["1"],
                "browser": [b"Chrome"],
                "version": [b"99.0.4844.84"],
                "mimetypes": [b""],
                "language": [b"en-US"],
                "platform": [b"MacIntel"],
                "vendor": [b"Google Inc."],
                "os": [b"Macintosh"],
            }
        }
    )

    assert ad_in.browser.enabled


@pytest.mark.parametrize("class_suffix", ["TokenHit", "TokenHistory"])
def test_override_hits_are_not_in_GeneralHistoryTokenTypes(class_suffix):
    """
    GeneralHistoryTokenTypes is a list of Literal's that contains all non-specialised
    TokenHit and TokenHistory. This test ensures a Hit or History are
    not "General" when they have been specialised.
    """
    all_classes = inspect.getmembers(models, inspect.isclass)
    hit_classes = {
        o[1].construct().token_type
        for o in filter(
            lambda name_class: name_class[0].endswith(class_suffix)
            and not name_class[0] == class_suffix,
            all_classes,
        )
    }
    assert (
        hit_classes.intersection(set(models.GeneralHistoryTokenType.__args__)) == set()
    )


@pytest.mark.parametrize("class_suffix", ["TokenRequest"])
def test_override_hits_are_not_in_BlankRequestTokenTypes(class_suffix):
    """
    BlankRequestTokenType is a list of Literal's that contains all non-specialised
    RequestToken. This test ensures a XXXTokenRequest is not "General" when
    they have been specialised.
    """
    all_classes = inspect.getmembers(models, inspect.isclass)
    request_classes_token_types = {
        o[1].construct().token_type
        for o in filter(
            lambda name_class: name_class[0].endswith(class_suffix)
            and not name_class[0] == class_suffix,
            all_classes,
        )
    }
    generic_requests = set(models.BlankRequestTokenType.__args__)
    assert request_classes_token_types.intersection(generic_requests) == set()


@pytest.mark.parametrize(
    "class_suffix,any_annotated_union",
    [
        ("TokenHit", AnyTokenHit),
        ("TokenHistory", AnyTokenHistory),
        ("TokenRequest", AnyTokenRequest),
        ("TokenResponse", AnyTokenResponse),
    ],
)
def test_XXXTokenYYY_are_registered_to_AnyTokenYYY(class_suffix, any_annotated_union):
    """
    Type annotations are leveraged to correctly parse dicts to XXXTokenHit,
    XXXTokenHistory, XXXTokenRequest's and this relies on them being part of the
    AnyTokenYYY types. This test enforces that.
    """
    all_classes = inspect.getmembers(models, inspect.isclass)

    set_of_hit_classes = {
        o[1]
        for o in filter(
            lambda name_class: name_class[0].endswith(class_suffix)
            and name_class[0] != class_suffix,
            all_classes,
        )
    }
    assert set_of_hit_classes == set(any_annotated_union.__args__[0].__args__)


def test_all_requests_have_a_response():
    all_classes = inspect.getmembers(models, inspect.isclass)

    set_of_request_classes = set(
        o[0].removesuffix("TokenRequest")
        for o in filter(
            lambda name_class: name_class[0].endswith("TokenRequest")
            and name_class[0] != "TokenRequest",
            all_classes,
        )
    )

    set_of_response_classes = set(
        o[0].removesuffix("TokenResponse")
        for o in filter(
            lambda name_class: name_class[0].endswith("TokenResponse")
            and name_class[0] != "TokenResponse",
            all_classes,
        )
    )
    assert not set_of_request_classes.isdisjoint(set_of_response_classes)


@pytest.mark.parametrize(
    "history_type, hit_type, seed_data, expected_data",
    [
        (
            WebBugTokenHistory,
            WebBugTokenHit,
            {
                "useragent": "python 3.10",
                "geo_info": GeoIPBogonInfo(ip="127.0.0.1", bogon=True),
            },
            {
                "location": None,
                "referer": None,
                "request_args": {},
                "request_headers": None,
                "useragent": "python 3.10",
            },
        ),
        (
            Log4ShellTokenHistory,
            Log4ShellTokenHit,
            {"src_data": {"log4_shell_computer_name": "computer_name"}},
            {"src_data": {"log4_shell_computer_name": "computer_name"}},
        ),
        (
            SMTPTokenHistory,
            SMTPTokenHit,
            {
                "mail": SMTPMailField(
                    sender="ender@test.com",
                    links=["https://link.found/in/mail"],
                    attachments=[],
                    recipients=[],
                    headers=[],
                    helo=SMTPHeloField(
                        client_name="test",
                        client_ip="123.4.5.6",
                    ),
                )
            },
            {
                "mail": json_safe_dict(
                    SMTPMailField(
                        sender="ender@test.com",
                        links=["https://link.found/in/mail"],
                        attachments=[],
                        recipients=[],
                        headers=[],
                        helo=SMTPHeloField(
                            client_name="test",
                            client_ip="123.4.5.6",
                        ),
                    )
                )
            },
        ),
    ],
)
def test_get_additional_data_for_webhook(
    history_type, hit_type, seed_data, expected_data
):
    hist = history_type(
        hits=[
            hit_type(
                time_of_hit=20,
                src_ip="127.0.0.1",
                is_tor_relay=True,
                input_channel="HTTP",
                **seed_data,
            )
        ]
    )
    assert expected_data == hist.get_additional_data_for_notification()


def test_download_content_types():
    assert (
        str(DownloadContentTypes.APPMSEXCELL) == DownloadContentTypes.APPMSEXCELL.value
    )


def test_download_msword_response():
    # TODO: these are not `BaseModels` and validation
    #       hooks have no effect. FIXME: to pass!
    # with pytest.raises(ValidationError):
    DownloadMSWordResponse(
        token="test",
        auth="sss",
        filename="nodotdocx.doc",
        content="stuff",
    )


def test_log_4_shell_token_response():
    resp = Log4ShellTokenResponse(
        auth_token="some_auth",
        token="sometoken",
        token_url="https://serv.org/sometoken",
        hostname="SRV01.local",
    )
    assert "jndi:ldap://" in resp.token_usage
    assert Log4ShellTokenResponse._token_marker in resp.token_with_usage_info


@pytest.mark.parametrize(
    "data,expect_success",
    [
        (
            {
                "token_type": TokenTypes.AWS_KEYS,
                "time_of_hit": 1652815479.13329,
                "src_ip": "196.61.107.19",
                "input_channel": "HTTP",
                "geo_info": {
                    "loc": "-34.0500,18.4833",
                    "city": "Cape Town",
                    "ip": "196.61.107.19",
                    "region": "Western Cape",
                    "timezone": "Africa/Johannesburg",
                    "country": "ZA",
                    "readme": "https://ipinfo.io/missingauth",
                    "org": "AS37363 Faircape",
                    "postal": "7805",
                },
                "is_tor_relay": False,
                "user_agent": "Boto3/1.23.3 Python/3.10.2 Linux/5.10.104-linuxkit Botocore/1.26.3",
                "additional_info": {
                    "AWS Key Log Data": {"eventName": ["GetCallerIdentity"]}
                },
            },
            True,
        ),
        (
            {
                "token_type": TokenTypes.AWS_KEYS,
                "time_of_hit": 1652815479.13329,
                "safety_net": True,
                "input_channel": "HTTP",
            },
            True,
        ),
        (
            {
                "token_type": TokenTypes.AWS_KEYS,
                "time_of_hit": 1652815479.13329,
                "safety_net": True,
                "input_channel": "HTTP",
                "is_tor_relay": False,
            },
            True,  # V2 compatibility requires this to parse error free
        ),
        (
            {
                "token_type": TokenTypes.AWS_KEYS,
                "time_of_hit": 1652815479.13329,
                "safety_net": False,
                "input_channel": "HTTP",
                "is_tor_relay": False,
            },
            True,  # V2 compatibility requires this to parse error free.
        ),
    ],
)
def test_aws_key_token_hits(data: dict, expect_success: bool):
    """Aws token can get triggered in one of two ways.
    'regular'  and 'safety_net'. In the regular way
    we get a bunch of information. In the 'safety_net' way
    we don't. This boils down to details of what AWS logs for varying
    AWS key usage: See: https://blog.thinkst.com/2022/02/a-safety-net-for-aws-canarytokens.html

    This test ensures we correctly parse both 'shapes'.

    Args:
        data (dict): payload to parse.
        expect_success (bool): Indicates the payload is correct / valid.
    """
    if expect_success:
        hit = parse_obj_as(AWSKeyTokenHit, data)
        if data.get("safety_net", False):
            assert hit.additional_info.aws_key_log_data["safety_net"] == [
                str(data["safety_net"])
            ]
            assert hit.safety_net
        else:
            assert not hit.safety_net
    else:
        with pytest.raises(ValidationError):
            _ = parse_obj_as(AWSKeyTokenHit, data)
