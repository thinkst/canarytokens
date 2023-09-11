from typing import Optional

import pytest

from canarytokens import tokens as t
from canarytokens.models import TokenTypes


@pytest.mark.parametrize(
    "query, username, hostname, domain, should_match,",
    [
        (
            "username1.hostname2.domain-3.ini.shxlva7y7c2kw4n0tl90kl6ve.canarytokens.org",
            "username1",
            "hostname2",
            "domain-3",
            True,
        ),
        (
            "username1.hostname2.domain-3.int.shxlva7y7c2kw4n0tl90kl6ve.canarytokens.org",
            "username1",
            "hostname2",
            "domain-3",
            False,
        ),
        (
            "username1.hostname2.ini.shxlva7y7c2kw4n0tl90kl6ve.canarytokens.org",
            "username1",
            "hostname2",
            "",
            True,
        ),
    ],
)
def test_windows_dir_pattern(
    query: str, username: str, hostname: str, domain: Optional[str], should_match: bool
):
    if (m := t.desktop_ini_browsing_pattern.match(query)) and m is not None:
        data = t.Canarytoken._desktop_ini_browsing(m)
        assert should_match
        assert data["src_data"] == {
            "windows_desktopini_access_username": username,
            "windows_desktopini_access_hostname": hostname,
            "windows_desktopini_access_domain": domain,
        }
    else:
        assert not should_match


@pytest.mark.parametrize(
    "query, computer_name, should_match,",
    [
        ("xbrokenpc.L4J.sometoken.com", "brokenpc", True),
        ("ns1.L4J.sometoken.com", "(not obtained)", True),
        ("xbrokenpc.L4.sometoken.com", "brokenpc", False),
    ],
)
def test_log4_shell_pattern(query, computer_name, should_match):
    if (m := t.log4_shell_pattern.match(query)) and m is not None:
        data = t.Canarytoken._log4_shell(m)
        assert should_match
        assert data["src_data"]["log4_shell_computer_name"] == computer_name
    else:
        assert not should_match


@pytest.mark.parametrize(
    "query, cmd_computer_name,cmd_user_name,should_match,",
    [
        ("cbrokenpc.UN.ubrokenuser.CMD.sometoken.com", "brokenpc", "brokenuser", True),
        ("c.UN.ubrokenuser.CMD.sometoken.com", "(not obtained)", "brokenuser", True),
        # ("xbrokenpc.L4.sometoken.com", "brokenpc", False),
    ],
)
def test_cmd_process_pattern(query, cmd_computer_name, cmd_user_name, should_match):
    if (m := t.cmd_process_pattern.match(query)) and m is not None:
        data = t.Canarytoken._cmd_process(m)
        assert should_match
        assert data["src_data"]["cmd_computer_name"] == cmd_computer_name
        assert data["src_data"]["cmd_user_name"] == cmd_user_name

    else:
        assert not should_match


def test_canarytoken_create_and_fetch():
    ct = t.Canarytoken()
    ct_new = t.Canarytoken(value=ct.value())
    assert ct_new.value() == ct.value()


@pytest.mark.parametrize(
    "token_type, hit_info",
    [
        (TokenTypes.DNS, {}),
        (
            TokenTypes.WINDOWS_DIR,
            {
                "src_data": {
                    "windows_desktopini_access_username": "username1",
                    "windows_desktopini_access_hostname": "hostname2",
                    "windows_desktopini_access_domain": "domain3",
                }
            },
        ),
        (
            TokenTypes.LOG4SHELL,
            {"src_data": {"log4_shell_computer_name": "server.com"}},
        ),
        (
            TokenTypes.CLONEDSITE,
            {"referer": "https://test.com", "location": "https://test.com"},
        ),
        (
            TokenTypes.ADOBE_PDF,
            {
                "token_type": TokenTypes.ADOBE_PDF,
                "time_of_hit": 1652815479.13329,
                "src_ip": "172.253.205.33",
                "geo_info": {
                    "loc": (51.5085, -0.1257),
                    "org": "AS15169 Google LLC",
                    "city": "London",
                    "country": "GB",
                    "region": "England",
                    "hostname": None,
                    "ip": "172.253.205.33",
                    "timezone": "Europe/London",
                    "postal": "EC1A",
                    "asn": None,
                },
                "is_tor_relay": False,
                "input_channel": "DNS",
                "src_data": {},
            },
        ),
        (TokenTypes.FAST_REDIRECT, {"useragent": "python 3.9"}),
        (
            TokenTypes.SLOW_REDIRECT,
            {
                "referer": "https://test.com",
                "location": "https://test.com",
                "useragent": "python 3.9",
            },
        ),
        (TokenTypes.KUBECONFIG, {"location": "/get", "useragent": "Unknown"}),
        (TokenTypes.MS_EXCEL, {}),
        (TokenTypes.MY_SQL, {"additional_info": ""}),
        (TokenTypes.QR_CODE, {}),
        (TokenTypes.SIGNED_EXE, {}),
        (
            TokenTypes.SMTP,
            {
                "mail": {
                    "sender": "me@test.com",
                    "recipients": ["you@test.com"],
                    "links": [],
                    "headers": [],
                    "attachments": [],
                    "helo": {
                        "client_name": "test",
                        "client_ip": "10.2.0.1",
                    },
                }
            },
        ),
        (TokenTypes.SVN, {}),
        (TokenTypes.WEB, {"useragent": "python3.6"}),
        (TokenTypes.WEB_IMAGE, {}),
        (
            TokenTypes.WIREGUARD,
            {
                "src_data": {
                    "src_port": 3333,
                    "server_public_key": b"sss",
                    "client_public_key": b"ytes",
                    "session_index": 123,
                }
            },
        ),
    ],
)
def test_create_token_hit(setup_db, token_type, hit_info):
    """
    Check that token hist creation works for all types.
    """
    input_channel = "DNS"
    src_ip = "127.0.0.1"

    _ = t.Canarytoken.create_token_hit(
        token_type,
        input_channel=input_channel,
        src_ip=src_ip,
        hit_info=hit_info,
    )


@pytest.mark.parametrize(
    "in_url, expected_out",
    [
        # regular payload of Hello2!
        ("JBSWY3DPGIQQ.G01.yh6wfyh752qi06e35f9b0260f.127.0.0.1", "Hello2!"),
        # mixed case
        ("JbSwy3DPgiQq.g01.yh6wfyh752qi06e35f9b0260f.127.0.0.1", "Hello2!"),
        # fails to decode utf-8; gets hexlified
        (
            "GE2QGIWC2NZYFRBEYVKFIJHU4Q.G01.yh6wfyh752qi06e35f9b0260f.127.0.0.1",
            "31350322c2d37382c424c5545424f4e4",
        ),
        # fails to decode base32; return raw (guaranteed decodable by channel_dns)
        (
            "A---------.G01.yh6wfyh752qi06e35f9b0260f.127.0.0.1",
            "Unrecoverable data: A---------",
        ),
    ],
)
def test_generic_data(in_url: str, expected_out: dict[str, str]):
    src_data = t.Canarytoken.look_for_source_data(in_url)
    assert src_data["src_data"]["generic_data"] == expected_out
