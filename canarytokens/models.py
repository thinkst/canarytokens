from __future__ import annotations

import enum
import json
import os
import re
import socket
from dataclasses import dataclass
from datetime import datetime
from distutils.util import strtobool
from functools import cached_property
from io import BytesIO
from ipaddress import IPv4Address
from tempfile import SpooledTemporaryFile
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)

from fastapi import Response
from pydantic import (
    BaseModel,
    ConstrainedInt,
    ConstrainedStr,
    EmailStr,
    Field,
    HttpUrl,
    root_validator,
    validator,
)
from pydantic.generics import GenericModel
from typing_extensions import Annotated

# DESIGN: We'll want a constraint on this but what is sensible as a user and what is practical for out system?
MEMO_MAX_CHARACTERS = 1000
# fmt: off
CANARYTOKEN_ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                        'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                        'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3',
                        '4', '5', '6', '7', '8', '9']
# fmt: on
CANARYTOKEN_LENGTH = 25  # equivalent to 128-bit id

CANARY_PDF_TEMPLATE_OFFSET: int = 793


class Memo(ConstrainedStr):
    max_length: int = MEMO_MAX_CHARACTERS


class Port(ConstrainedInt):
    ge: int = 0
    lt: int = 65535


class Hostname(ConstrainedStr):
    max_length: int = 253
    regex = re.compile(
        r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{1,61}[a-zA-Z0-9])\.){1,61}([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]{1,61}[A-Za-z0-9]){1,253}$"
    )


class PseudoUrl(ConstrainedStr):
    """
    Clonedweb token can get used where the `referer`
    sent in the token is a pseudo url. Currently, only
    "about:blank" is supported / known case.
    """

    regex = re.compile(r"^about:blank$")


@dataclass()
class V2:
    """Indicates models should exhibit V2 behavior"""

    # DESIGN: This separation might be short lived. If not we can do better.
    version = "v2"
    canarytokens_sld: str
    canarytokens_domain: str
    canarytokens_dns_port: int
    canarytokens_http_port: Optional[int]
    scheme: Literal["http", "https"]

    @property
    def live(self) -> bool:
        """Used to indicate tests are targeting a live server.
        Live means nginx is routing to switchboard and dns resolves.
        """
        return strtobool(os.getenv("LIVE", "FALSE"))

    @property
    def server_url(self) -> HttpUrl:  # pragma: no cover
        return HttpUrl(
            url=f"{self.scheme}://{self.canarytokens_sld}", scheme=self.scheme
        )

    @cached_property
    def canarytokens_ips(self) -> list[str]:  # pragma: no cover
        *_, ips = socket.gethostbyname_ex(self.canarytokens_domain)
        return ips


@dataclass()
class V3:
    """Indicates models should exhibit V3 behavior"""

    # A near replica of V2 but it wasn't always.
    # Both are set to get removed.
    version = "v3"
    canarytokens_sld: str
    canarytokens_domain: str
    canarytokens_dns_port: int
    canarytokens_http_port: Optional[int]
    scheme: Literal["http", "https"]

    @property
    def server_url(self) -> HttpUrl:  # pragma: no cover
        return HttpUrl(
            url=f"{self.scheme}://{self.canarytokens_sld}", scheme=self.scheme
        )

    @cached_property
    def canarytokens_ips(self) -> list[str]:  # pragma: no cover
        *_, ips = socket.gethostbyname_ex(self.canarytokens_domain)
        return ips

    @property
    def live(self) -> bool:
        return strtobool(os.getenv("LIVE", "FALSE"))


class KubeCerts(TypedDict):
    """Kube digest (f), cert (c) and key (k) are stored directly and not
    base64 encoded.
    """

    f: bytes  # mTLS digest
    c: bytes  # Cert
    k: bytes  # Key


class TokenTypes(str, enum.Enum):
    """Enumerates all supported token types"""

    WEB = "web"
    DNS = "dns"
    WEB_IMAGE = "web_image"
    MS_WORD = "ms_word"
    MS_EXCEL = "ms_excel"
    ADOBE_PDF = "adobe_pdf"
    WIREGUARD = "wireguard"
    WINDOWS_DIR = "windows_dir"
    CLONEDSITE = "clonedsite"
    QR_CODE = "qr_code"
    SVN = "svn"
    SMTP = "smtp"
    SQL_SERVER = "sql_server"
    MY_SQL = "my_sql"
    AWS_KEYS = "aws_keys"
    SIGNED_EXE = "signed_exe"
    FAST_REDIRECT = "fast_redirect"
    SLOW_REDIRECT = "slow_redirect"
    KUBECONFIG = "kubeconfig"
    LOG4SHELL = "log4shell"

    def __str__(self) -> str:
        return str(self.value)


GeneralHistoryTokenType = Literal[
    "blank"
    # TokenTypes.DNS,
    # TokenTypes.FAST_REDIRECT,
    # These have been specialised.
    # TokenTypes.KUBECONFIG,
    # TokenTypes.SQL_SERVER,
    # TokenTypes.MS_WORD,
    # TokenTypes.WEB_IMAGE,
    # TokenTypes.AWS_KEYS,
    # TokenTypes.KUBECONFIG,
    # TokenTypes.ADOBE_PDF,
    # TokenTypes.MS_EXCEL,
    # TokenTypes.SVN,
    # TokenTypes.SIGNED_EXE,
    # TokenTypes.QR_CODE,
    # TokenTypes.WIREGUARD,
    # TokenTypes.WEB,
    # TokenTypes.MY_SQL,
    # TokenTypes.SLOW_REDIRECT,
    # TokenTypes.SMTP,
    # TokenTypes.CLONEDSITE,
    # TokenTypes.LOG4SHELL,
]

BlankRequestTokenType = Literal[
    "blank",
    # TokenTypes.QR_CODE,
    # These have been specialised.
    # TokenTypes.KUBECONFIG,
    # TokenTypes.SQL_SERVER,
    # TokenTypes.ADOBE_PDF,
    # TokenTypes.MS_EXCEL,
    # TokenTypes.WEB_IMAGE,
    # TokenTypes.KUBECONFIG,
    # TokenTypes.AWS_KEYS,
    # TokenTypes.ADOBE_PDF,
    # TokenTypes.SVN,
    # TokenTypes.SIGNED_EXE,
    # TokenTypes.WINDOWS_DIR,
    # TokenTypes.FAST_REDIRECT,
    # TokenTypes.DNS,
    # TokenTypes.WIREGUARD,
    # TokenTypes.WEB,
    # TokenTypes.MY_SQL,
    # TokenTypes.SLOW_REDIRECT,
    # TokenTypes.SMTP,
    # TokenTypes.CLONEDSITE,
    # TokenTypes.LOG4SHELL,
]


def json_safe_dict(m: BaseModel, exclude: Tuple = ()) -> Dict[str, str]:
    return json.loads(m.json(exclude_none=True, exclude=set(exclude)))


class TokenRequest(BaseModel):
    """
    TokenRequest holds fields needed to create a Canarytoken.
    """

    # token_type: BlankRequestTokenType
    email: Optional[EmailStr]
    webhook_url: Optional[HttpUrl]
    memo: Memo

    def __init__(__pydantic_self__, **data: Any) -> None:
        # TODO: fix this on the frontend - but for now we'll handle it here
        # For handling v2 specific code.
        if data.get("email", False) == "":  # pragma: no cover
            data.pop("email")

        if data.get("webhook_url", False) == "":  # pragma: no cover
            data.pop("webhook_url")

        if isinstance(data.get("token_type", None), str):
            data["token_type"] = TokenTypes(data["token_type"])

        super().__init__(**data)

    @root_validator
    def check_email_or_webhook_opt(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not (values.get("webhook_url") or values.get("email")):
            raise ValueError("either webhook or email is required")
        return values

    # Design: this might be short lived. If not we can do better.
    # Singledispatch if it plays well with pydantic.
    def to_dict(self, version: Union[V2, V3]) -> Dict[str, Any]:
        if isinstance(version, V2):
            return self.v2_dict()
        elif isinstance(version, V3):
            return json_safe_dict(self)
        raise NotImplementedError("version must used.")

    def v2_dict(self) -> Dict[str, Any]:
        webhook_url = self.webhook_url or ""
        out_dict = {
            "type": getattr(self, "token_type").value,
            "email": self.email or "",
            "memo": self.memo,
            "webhook": str(webhook_url),
        }
        if "redirect_url" in self.dict():  # pragma: no cover
            out_dict["redirect_url"] = self.redirect_url  # type: ignore
        return out_dict

    def json_safe_dict(self) -> Dict[str, str]:
        return json_safe_dict(self)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {TokenTypes: lambda v: v.value}


class AWSKeyTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS


class QRCodeTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE


class DNSTokenRequest(TokenRequest):
    """"""

    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS

    class Config:

        schema_extra = {
            "example": {
                "token_type": TokenTypes.DNS,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "webhook_url": "https://hooks.slack.com/test",
            },
        }


class PDFTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF


class KubeconfigTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.KUBECONFIG] = TokenTypes.KUBECONFIG


class MsWordDocumentTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD


class MsExcelDocumentTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.MS_EXCEL] = TokenTypes.MS_EXCEL


class SvnTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SVN] = TokenTypes.SVN


class UploadedExe(BaseModel):
    content_type: Literal["application/x-msdownload", "application/octet-stream"]
    filename: str
    file: SpooledTemporaryFile

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class CustomBinaryTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    signed_exe: UploadedExe

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            SpooledTemporaryFile: lambda v: v.__dict__,
            BytesIO: lambda v: v.__dict__,
        }


class UploadedImage(BaseModel):
    content_type: Literal["image/png", "image/gif", "image/jpg"]
    filename: str
    file: SpooledTemporaryFile

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class CustomImageTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    web_image: UploadedImage

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            SpooledTemporaryFile: lambda v: v.__dict__,
            BytesIO: lambda v: v.__dict__,
        }


class WebBugTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB


class ClonedWebTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    clonedsite: str


class FastRedirectTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT
    redirect_url: str

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.FAST_REDIRECT,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "redirect_url": "https://youtube.com",
            },
        }


class SlowRedirectTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SLOW_REDIRECT] = TokenTypes.SLOW_REDIRECT
    # TODO: tighten this up so redirects are validated
    # https://github.com/thinkst/canarytokens/issues/122
    redirect_url: str

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.SLOW_REDIRECT,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "redirect_url": "https://youtube.com",
            },
        }


class Log4ShellTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.LOG4SHELL,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "webhook_url": "https://hooks.slack.com/test",
            },
        }


class SMTPTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP


class WireguardTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WIREGUARD] = TokenTypes.WIREGUARD


class MySQLTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.MY_SQL] = TokenTypes.MY_SQL


class SQLServerTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER
    sql_server_sql_action: Optional[Literal["INSERT", "DELETE", "UPDATE", "SELECT"]]
    sql_server_table_name: str = "TABLE1"
    sql_server_view_name: str = "VIEW1"
    sql_server_function_name: str = "FUNCTION1"
    sql_server_trigger_name: str = "TRIGGER1"


class WindowsDirectoryTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR


AnyTokenRequest = Annotated[
    Union[
        FastRedirectTokenRequest,
        QRCodeTokenRequest,
        AWSKeyTokenRequest,
        PDFTokenRequest,
        DNSTokenRequest,
        Log4ShellTokenRequest,
        SMTPTokenRequest,
        ClonedWebTokenRequest,
        WindowsDirectoryTokenRequest,
        WebBugTokenRequest,
        SlowRedirectTokenRequest,
        MySQLTokenRequest,
        WireguardTokenRequest,
        CustomBinaryTokenRequest,
        CustomImageTokenRequest,
        SvnTokenRequest,
        MsWordDocumentTokenRequest,
        MsExcelDocumentTokenRequest,
        SQLServerTokenRequest,
        KubeconfigTokenRequest,
    ],
    Field(discriminator="token_type"),
]


class TokenResponse(BaseModel):
    # token_type: Literal["blank"] = "blank"
    token: str
    # TODO: make host name validation stricter
    hostname: Hostname
    token_url: Union[HttpUrl, Literal[""]]
    auth_token: str
    email: Union[EmailStr, Literal[""]] = ""
    webhook_url: Union[HttpUrl, Literal[""]] = ""

    # Design: Existing tokens server returns these additional fields
    # are they needed?
    url_components: Optional[List[List[str]]]
    error: Optional[str]
    error_message: Optional[str]
    # Used by tokenCheck script.
    # Aliased to token_url
    Url: Union[HttpUrl, Literal[""], None]

    @root_validator(pre=True)
    # TODO: fix pydantic vs mypy - it's possible
    def normalize_names(cls, values: dict[str, Any]) -> dict[str, any]:  # type: ignore
        keys_to_convert = [
            # TODO: make is consistent.
            ("Auth", "auth_token"),
            ("Url", "token_url"),
        ]
        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values and values[old_key] is not None:
                values[new_key] = values.get(old_key)

        return {k: v for k, v in values.items()}

    def __init__(__pydantic_self__, **data: Any) -> None:
        data["webhook_url"] = data.pop("webhook", "")
        data["Url"] = data["token_url"]
        super().__init__(**data)


class AWSKeyTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    output: str


class PDFTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF
    hostname: str  # Hostname Local testing fails this check TODO: FIXME


class QRCodeTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE
    qrcode_png: str


class DNSTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.DNS,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "webhook_url": "https://hooks.slack.com/test",
            },
        }


class KubeconfigTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.KUBECONFIG] = TokenTypes.KUBECONFIG
    kubeconfig: str

    def __init__(__pydantic_self__, **data: Any) -> None:
        scheme = "http"
        host = "hostname.com"
        token = "random1token2string4test5"

        if "Hostname" in data:  # pragma: no cover
            data["hostname"] = data.pop("Hostname")
        if "Url_components" in data:  # pragma: no cover
            data["url_components"] = data.pop("Url_components")
        if "Url" in data:  # pragma: no cover
            data["token_url"] = data.pop("Url")

        if data.get("hostname", "") == "":  # pragma: no cover
            data["hostname"] = "{token}.{host}".format(token=token, host=host)

        if data.get("url_components", "") == "":  # pragma: no cover
            data["url_components"] = None

        if data.get("token_url", "") == "":  # pragma: no cover
            data["token_url"] = "{scheme}://{host}/static/{token}/post.jsp".format(
                scheme=scheme, host=host, token=token
            )

        super().__init__(**data)


class CustomImageTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE


class MsWordDocumentTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD


class MsExcelDocumentTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.MS_EXCEL] = TokenTypes.MS_EXCEL


class SvnTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SVN] = TokenTypes.SVN


class CustomBinaryTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    file_name: str
    file_contents: str
    hostname: str  # Hostname Local testing fails this check on NXDOMAIN TODO: FIXME

    @validator("file_contents", pre=True)
    def check_file_contents(cls, file_contents: str, values: dict[str, Any]) -> str:
        if not file_contents.startswith("data:octet/stream;base64"):
            raise ValueError("File contents must be base64 encoded")
        return file_contents


class WebBugTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB


class SQLServerTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER


class ClonedWebTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    clonedsite_js: Optional[str]


class FastRedirectTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.DNS,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "webhook_url": "https://hooks.slack.com/test",
            },
        }


class SlowRedirectTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SLOW_REDIRECT] = TokenTypes.SLOW_REDIRECT


class Log4ShellTokenResponse(TokenResponse):
    # DESIGN: These 2 markers should be application constants.
    #         keeping here until they are needed elsewhere.
    _hostname_marker: Literal["x"] = "x"
    _token_marker: Literal["L4J"] = "L4J"
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL
    token_usage: str
    token_with_usage_info: str
    # src_data: dict[str, str]

    @root_validator(pre=True)
    def set_token_usage_info(cls, values: dict[str, Any]) -> dict[str, any]:  # type: ignore
        values[
            "token_with_usage_info"
        ] = f"{cls._hostname_marker}{{hostname}}.{cls._token_marker}.{values['hostname']}"
        return values

    @root_validator(pre=True)
    def set_token_usage(cls, values: dict[str, Any]) -> dict[str, any]:  # type: ignore
        values[
            "token_usage"
        ] = f"${{jndi:ldap://{cls._hostname_marker}${{hostName}}.{cls._token_marker}.{values['hostname']}/a}}"
        return values

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.LOG4SHELL,
                "memo": "Added to user login portal.",
                "email": "username@domain.com",
                "webhook_url": "https://hooks.slack.com/test",
            },
        }


class WindowsDirectoryTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR


class SMTPTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    unique_email: Optional[EmailStr]

    # FIXME: validate all
    @validator("unique_email", pre=True)
    def set_unique_email(
        cls, unique_email: Optional[EmailStr], values: dict[str, Any]
    ) -> EmailStr:
        if unique_email is None:
            # TODO: mapping from hostname to domain should in some common code
            #       if we do this often.
            if "127.0.0.1" in values["hostname"]:
                domain = "localhost.com"
            else:
                domain = ".".join(values["hostname"].split(".")[-2:])
            return EmailStr(f"{values['token']}@{domain}")
        return unique_email


class WireguardTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WIREGUARD] = TokenTypes.WIREGUARD
    wg_conf: str
    qr_code: str


class MySQLTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.MY_SQL] = TokenTypes.MY_SQL
    usage: Optional[str]


AnyTokenResponse = Annotated[
    Union[
        CustomImageTokenResponse,
        SMTPTokenResponse,
        SvnTokenResponse,
        CustomBinaryTokenResponse,
        SlowRedirectTokenResponse,
        AWSKeyTokenResponse,
        MsWordDocumentTokenResponse,
        Log4ShellTokenResponse,
        MsExcelDocumentTokenResponse,
        QRCodeTokenResponse,
        PDFTokenResponse,
        DNSTokenResponse,
        MySQLTokenResponse,
        WireguardTokenResponse,
        WindowsDirectoryTokenResponse,
        FastRedirectTokenResponse,
        ClonedWebTokenResponse,
        WebBugTokenResponse,
        SQLServerTokenResponse,
        DNSTokenResponse,
        Log4ShellTokenResponse,
        AWSKeyTokenResponse,
        PDFTokenResponse,
        SlowRedirectTokenResponse,
        CustomBinaryTokenResponse,
        CustomImageTokenResponse,
        SvnTokenResponse,
        MsWordDocumentTokenResponse,
        MsExcelDocumentTokenResponse,
        KubeconfigTokenResponse,
    ],
    Field(discriminator="token_type"),
]


class PageRequest(BaseModel):
    token: str
    auth: str


class HistoryPageRequest(PageRequest):
    """
    A Canarytoken `token` and it's associated `auth`
    to request the history page.
    """

    ...


class ManagePageRequest(PageRequest):
    """
    A Canarytoken `token` and it's associated `auth`
    to request the manage page.
    """

    ...


class ASN(BaseModel):
    route: str  # '41.1.0.0/18
    type: str  # 'isp
    asn: str  # 'AS29975'
    domain: str  # 'vodacom.com'
    name: str  # 'Vodacom'


class GeoIPBogonInfo(BaseModel):
    ip: str
    bogon: Literal[True]


class GeoIPInfo(BaseModel):
    # DESIGN/TODO: This is based on 3rd party response. Make all fields optional / match the api we expecting
    loc: Tuple[float, float]  # '-33.9778,18.6167'
    org: Optional[str]  # 'AS29975 Vodacom'
    city: str  # 'Cape Town'
    # TODO: Validate contry code pycountry?? add a dependency for this??
    country: str  # 'ZA',
    region: str  # 'Western Cape'
    #  TODO: validate this domain
    hostname: Optional[str]  # 'dnsinfo1-cte-pt.3g.vodacom.co.za
    ip: str  # '41.1.47.253
    timezone: str  # 'Africa/Johannesburg
    postal: Optional[str]  # '7100 or EC1A
    asn: Optional[
        ASN
    ]  # {'route': '41.1.0.0/18', 'type': 'isp', 'asn': 'AS29975', 'domain': 'vodacom.com', 'name': 'Vodacom'}
    readme: Optional[str]
    # bogon

    @validator("loc", pre=True)
    def validator_loc(loc: Union[str, list]) -> Tuple[float, float]:  # type: ignore
        # TODO: fix pydantic vs mypy - it's possible
        if isinstance(loc, str):
            lon, lat = loc.split(",")
        elif isinstance(loc, list):
            lon, lat = loc
        elif isinstance(loc, tuple):
            return loc
        else:
            raise TypeError(f"loc must be str or list: {type(loc)} was given. {loc}")
        return (float(lon), float(lat))

    def dict(
        self,
        *,
        include: 'Union["AbstractSetIntStr", "MappingIntStrAny"]' = None,  # noqa F821
        exclude: 'Union["AbstractSetIntStr", "MappingIntStrAny"]' = None,  # noqa F821
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":  # noqa F821
        data = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        # V2 Compatible serialization
        data["loc"] = ",".join([f"{o:.4f}" for o in self.loc])
        return data

    class Config:
        json_encoders = {
            list: lambda v: ",".join(v),
        }


class ServiceInfo(BaseModel):
    version: list[str]
    enabled: list[str]
    installed: list[str]
    r: Optional[list[str]]
    l: Optional[list[str]]


class BrowserInfo(BaseModel):
    mimetypes: list[str]
    vendor: list[str]
    language: list[str]
    enabled: list[str]
    installed: list[str]
    platform: list[str]
    version: list[str]
    os: list[str]
    browser: list[str]
    r: Optional[list[str]]
    l: Optional[list[str]]


class AWSKeyAdditionalInfo(BaseModel):
    aws_key_log_data: dict[str, list[str]]

    @root_validator(pre=True)
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, any]:  # type: ignore
        keys_to_convert = [
            # TODO: make this consistent.
            ("AWS Key Log Data", "aws_key_log_data"),
        ]
        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values:
                values[new_key] = values.pop(old_key)

        return {k.lower(): v for k, v in values.items()}


class AdditionalInfo(BaseModel):
    # the ServiceInfo keys are dynamic
    # this only works for our test
    javascript: Optional[ServiceInfo]
    browser: Optional[BrowserInfo]
    # TODO: split this off - additional info can be handled separately.
    #       See `AWSKeyAdditionalInfo`
    mysql_client: Optional[dict[str, list[str]]]

    def serialize_for_v2(self) -> dict:
        data = json_safe_dict(self)
        if "browser" in data:
            data["Browser"] = data.pop("browser")
        if "javascript" in data:
            data["Javascript"] = data.pop("javascript")
        if "mysql_client" in data:
            data["MySQL Client"] = data.pop("mysql_client")
        return data

    @root_validator(pre=True)
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, any]:  # type: ignore
        keys_to_convert = [
            # TODO: make is consistent.
            ("MySQL Client", "mysql_client"),
        ]

        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values:
                values[new_key] = values.pop(old_key)

        return {k.lower(): v for k, v in values.items()}


class SMTPHeloField(BaseModel):
    client_name: str
    client_ip: IPv4Address

    class Config:
        json_encoders = {
            IPv4Address: lambda v: str(v),
        }


class SMTPMailField(BaseModel):
    sender: EmailStr
    recipients: List[EmailStr]
    links: List[str]
    headers: List[str]
    helo: SMTPHeloField
    attachments: List[str]

    def dict(
        self,
        *,
        include: 'Union["AbstractSetIntStr", "MappingIntStrAny"]' = None,  # noqa F821
        exclude: 'Union["AbstractSetIntStr", "MappingIntStrAny"]' = None,  # noqa F821
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":  # noqa F821
        data = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        # V2 Compatible serialization
        data["recipients"] = [f"<{o}>" for o in data["recipients"]]
        return data


class TokenHit(BaseModel):
    # token_type: GeneralHistoryTokenType
    time_of_hit: float
    src_ip: Optional[str]
    geo_info: Union[GeoIPInfo, GeoIPBogonInfo, None, Literal[""]]
    is_tor_relay: Optional[bool]
    input_channel: str
    src_data: Optional[dict]  # v2 stores empty {} src_data for tokens without src_data.
    useragent: Optional[str]

    @validator("geo_info", pre=True)
    def adjust_geo_info(cls, value):
        # Allow loading v2 data.
        if value == "":
            return None
        return value


class AWSKeyTokenHit(TokenHit):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    useragent: Optional[str] = Field(
        None, alias="user_agent"
    )  # V2 does / did not store user agent.
    additional_info: Optional[AWSKeyAdditionalInfo]

    class Config:
        allow_population_by_field_name = True

    @property
    def safety_net(self):
        if self.additional_info is None:
            return False
        if safety_net := self.additional_info.aws_key_log_data.get("safety_net", False):
            if isinstance(safety_net, list):
                return strtobool(safety_net[0])
        return False

    def serialize_for_v2(self) -> dict:
        """Serialize an `AWSKeyTokenHit` into a dict
        that holds the equivalent info in the v2 shape.
        Returns:
            dict: AWSKeyTokenHit in v2 dict representation.
        """
        data = json_safe_dict(self, exclude=("token_type", "time_of_hit"))
        if "additional_info" in data and "aws_key_log_data" in data["additional_info"]:
            data["additional_info"]["AWS Key Log Data"] = data["additional_info"].pop(
                "aws_key_log_data"
            )
        if "user_agent" in data:
            data["useragent"] = data.pop("user_agent")
        return data

    def __init__(__pydantic_self__, **data):
        # Only for V2 compatibility.
        if not data.get("geo_info", False):
            data["geo_info"] = ""
        if not data.get("is_tor_relay", False):
            data["is_tor_relay"] = False
        if data.get("safety_net", False):
            additional_info = data.get("additional_info", {})
            log_data = additional_info.get("AWS Key Log Data", {})
            log_data.update({"safety_net": [str(data["safety_net"])]})
            data["additional_info"] = {"AWS Key Log Data": log_data}
        super().__init__(**data)

    @root_validator(allow_reuse=True)
    def validate_extras(cls, values):
        dependent_vals = [
            # "src_ip", #V2 stores src_ip as "". It's not None.
            # "geo_info",  #V2 stores geo info as "" on some hits.
            # "is_tor_relay", #V2 stores `is_tor_relay` on some hits even if src_ip is not there.
            # "user_agent", #V2 Does not store user agent for all hits
            # "additional_info", #V2 stores empty additional data. It's not None.
        ]

        if values.get("safety_net", False) or not values.get("src_ip", False):
            for x in dependent_vals:
                if values.get(x, None) is not None:
                    raise TypeError(f"{x} should be None when safety_net=True")
        else:
            for x in dependent_vals:
                if values.get(x, None) is None:
                    raise TypeError(f"{x} should not be None when safety_net=False")
        return values


class DNSTokenHit(TokenHit):
    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS


class PDFTokenHit(TokenHit):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF


class SMTPTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    mail: SMTPMailField


class KubeconfigTokenHit(TokenHit):
    token_type: Literal[TokenTypes.KUBECONFIG] = TokenTypes.KUBECONFIG
    location: str
    useragent: str


class MsWordDocumentTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD
    useragent: str


class WindowsDirectoryTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR
    src_data: Optional[dict[str, str]]


class MsExcelDocumentTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MS_EXCEL] = TokenTypes.MS_EXCEL
    useragent: Optional[str]


class SvnTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SVN] = TokenTypes.SVN


class SQLServerTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER


class WebBugTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB
    useragent: str
    additional_info: AdditionalInfo = AdditionalInfo()

    class Config:
        allow_population_by_field_name = True


class CustomImageTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    additional_info: AdditionalInfo = AdditionalInfo()
    useragent: Optional[str]


class ClonedWebTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    # TODO fix API spelling to 'referrer' (comes from JS document.referrer)
    referer: Union[HttpUrl, PseudoUrl]
    location: HttpUrl


class SlowRedirectTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SLOW_REDIRECT] = TokenTypes.SLOW_REDIRECT
    referer: Union[PseudoUrl, HttpUrl]
    location: HttpUrl
    useragent: str
    additional_info: AdditionalInfo = AdditionalInfo()


class FastRedirectTokenHit(TokenHit):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT
    referer: Union[PseudoUrl, HttpUrl, None]
    location: Optional[HttpUrl]
    useragent: str
    additional_info: AdditionalInfo = AdditionalInfo()


class Log4ShellTokenHit(TokenHit):
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL
    src_data: dict[str, str]


class QRCodeTokenHit(TokenHit):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE
    useragent: Optional[str]


class CustomBinaryTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE


class MySQLTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MY_SQL] = TokenTypes.MY_SQL
    additional_info: Optional[AdditionalInfo]


class WireguardSrcData(TypedDict):
    src_port: int
    server_public_key: bytes
    client_public_key: bytes
    session_index: int


class WireguardTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WIREGUARD] = TokenTypes.WIREGUARD
    src_data: WireguardSrcData


AnyTokenHit = Annotated[
    Union[
        DNSTokenHit,
        AWSKeyTokenHit,
        PDFTokenHit,
        ClonedWebTokenHit,
        Log4ShellTokenHit,
        SlowRedirectTokenHit,
        FastRedirectTokenHit,
        SMTPTokenHit,
        WebBugTokenHit,
        MySQLTokenHit,
        WireguardTokenHit,
        QRCodeTokenHit,
        CustomBinaryTokenHit,
        CustomImageTokenHit,
        SvnTokenHit,
        KubeconfigTokenHit,
        MsWordDocumentTokenHit,
        MsExcelDocumentTokenHit,
        WindowsDirectoryTokenHit,
        SQLServerTokenHit,
        KubeconfigTokenHit,
    ],
    Field(discriminator="token_type"),
]

TH = TypeVar("TH", bound=AnyTokenHit)


class TokenHistory(GenericModel, Generic[TH]):
    """
    TokenHistory holds the format of each tokens'hits.
    `token_type` dictates which type of token a
    the history represents. Most tokens differ in the history
    they collect and specialized XXXTokenHistory classes capture
    this.
    `hits` is a list containing all gather info from tokens firing.
    """

    hits: List[TH] = []

    def __init__(__pydantic_self__, **data: Any) -> None:
        token_type = data.pop(
            "token_type", __pydantic_self__.__fields__["token_type"].default
        )
        if (hits := data.get("hits", None)) is None:
            hits = []
            for time_of_hit, hit_details in data.items():
                hit_details["token_type"] = token_type
                hits.append({"time_of_hit": float(time_of_hit), **hit_details})
        super().__init__(hits=hits, token_type=token_type)

    def serialize_for_v2(self, readable_time_format: bool = False) -> dict[str, str]:
        """Serialize TokenHistory into the same shape as
        used by v2.
        """
        data = {}
        for hit in self.hits:
            if isinstance(hit, AWSKeyTokenHit):
                hit_data = hit.serialize_for_v2()
            else:
                hit_data = json_safe_dict(hit, exclude=("token_type", "time_of_hit"))
                if "additional_info" in hit_data:
                    hit_data["additional_info"] = hit.additional_info.serialize_for_v2()

            if not hit_data.get(
                "additional_info", True
            ):  # V2 does not store empty {} additional data.
                hit_data.pop("additional_info")
            if hit_data.get("geo_info", None) is None:
                hit_data["geo_info"] = ""
            if not hit_data.get("src_ip", None):
                hit_data.pop("geo_info", None)
            if not hit_data.get("src_ip", None):
                hit_data.pop("is_tor_relay", None)
            if readable_time_format:
                data[
                    datetime.fromtimestamp(hit.time_of_hit).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ] = hit_data
            else:
                data[f"{hit.time_of_hit:.6f}"] = hit_data
        return data

    def get_additional_data_for_notification(self) -> Dict[str, Any]:
        """
        Some tokens have additional info that should be included
        in webhook notifications. The dict returned from this function
        is included in webhook outputs.

        Returns:
            Dict[str, str]: Key value pairs to include in webhook info.
        """
        return {}

    def latest_hit(self) -> Optional[TH]:
        if len(self.hits) == 0:
            return None
        return sorted(self.hits, key=lambda o: o.time_of_hit)[-1]


class AWSKeyTokenHistory(TokenHistory[AWSKeyTokenHit]):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    hits: List[AWSKeyTokenHit]


class DNSTokenHistory(TokenHistory[DNSTokenHit]):
    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS
    hits: List[DNSTokenHit]


class PDFTokenHistory(TokenHistory[PDFTokenHit]):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF
    hits: List[PDFTokenHit]


class SlowRedirectTokenHistory(TokenHistory[SlowRedirectTokenHit]):
    token_type: Literal[TokenTypes.SLOW_REDIRECT] = TokenTypes.SLOW_REDIRECT
    hits: List[SlowRedirectTokenHit]


class FastRedirectTokenHistory(TokenHistory[FastRedirectTokenHit]):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT
    hits: List[FastRedirectTokenHit]


class CustomImageTokenHistory(TokenHistory[CustomImageTokenHit]):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    hits: List[CustomImageTokenHit] = []


class WindowsDirectoryTokenHistory(TokenHistory[WindowsDirectoryTokenHit]):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR
    hits: List[WindowsDirectoryTokenHit] = []


class CustomBinaryTokenHistory(TokenHistory[CustomBinaryTokenHit]):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    hits: List[CustomBinaryTokenHit] = []


class SQLServerTokenHistory(TokenHistory[SQLServerTokenHit]):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER
    hits: List[SQLServerTokenHit]


class WebBugTokenHistory(TokenHistory[WebBugTokenHit]):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB
    hits: List[WebBugTokenHit] = []

    def get_additional_data_for_notification(self) -> Dict[str, str]:
        """WebBug token extra info to inject into webhook and email
        notifications.

        Returns:
            Dict[str, str]: Key value pairs to include in webhook / email info.
        """
        latest_hit = self.latest_hit()
        if latest_hit is None:
            return {}
        return {"useragent": latest_hit.useragent}


class ClonedWebTokenHistory(TokenHistory[ClonedWebTokenHit]):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    hits: List[ClonedWebTokenHit] = []


class Log4ShellTokenHistory(TokenHistory[Log4ShellTokenHit]):
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL
    hits: List[Log4ShellTokenHit] = []

    def get_additional_data_for_notification(self) -> Dict[str, str]:
        """
        Adds the most recent hit's `src_data` to the
        webhook / email notification.

        Returns:
            Dict[str, str]: Key value pairs to include in webhook / email info.
        """
        latest_hit = self.latest_hit()
        if latest_hit is None:
            return {}
        # V2 has a src_data key added for compatibility.
        return {"src_data": latest_hit.src_data}


class QRCodeTokenHistory(TokenHistory[QRCodeTokenHit]):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE


class SMTPTokenHistory(TokenHistory[SMTPTokenHit]):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    hits: List[SMTPTokenHit] = []

    def get_additional_data_for_notification(self) -> Dict[str, Dict[str, str]]:
        most_recent_hit = sorted(self.hits, key=lambda o: o.time_of_hit)[-1]
        return {"mail": json_safe_dict(most_recent_hit.mail)}


class WireguardTokenHistory(TokenHistory[WireguardTokenHit]):
    token_type: Literal[TokenTypes.WIREGUARD] = TokenTypes.WIREGUARD
    hits: List[WireguardTokenHit] = []


class MySQLTokenHistory(TokenHistory[MySQLTokenHit]):
    token_type: Literal[TokenTypes.MY_SQL] = TokenTypes.MY_SQL
    hits: List[MySQLTokenHit]


class KubeconfigTokenHistory(TokenHistory[KubeconfigTokenHit]):
    token_type: Literal[TokenTypes.KUBECONFIG] = TokenTypes.KUBECONFIG
    hits: List[KubeconfigTokenHit] = []


class MsWordDocumentTokenHistory(TokenHistory[MsWordDocumentTokenHit]):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD
    hits: List[MsWordDocumentTokenHit] = []


class MsExcelDocumentTokenHistory(TokenHistory[MsExcelDocumentTokenHit]):
    token_type: Literal[TokenTypes.MS_EXCEL] = TokenTypes.MS_EXCEL
    hits: List[MsExcelDocumentTokenHit] = []


class SvnTokenHistory(TokenHistory[SvnTokenHit]):
    token_type: Literal[TokenTypes.SVN] = TokenTypes.SVN
    hits: List[SvnTokenHit] = []


# AnyTokenHistory is used to type annotate functions that
# handle any token history. It makes use of an annotated type
# that discriminates on `token_type` so pydantic can parse
# TokenHistory where they differ only in `token_type`.
AnyTokenHistory = Annotated[
    Union[
        DNSTokenHistory,
        AWSKeyTokenHistory,
        PDFTokenHistory,
        SMTPTokenHistory,
        ClonedWebTokenHistory,
        Log4ShellTokenHistory,
        SlowRedirectTokenHistory,
        FastRedirectTokenHistory,
        WebBugTokenHistory,
        CustomBinaryTokenHistory,
        WireguardTokenHistory,
        QRCodeTokenHistory,
        MySQLTokenHistory,
        CustomImageTokenHistory,
        SvnTokenHistory,
        KubeconfigTokenHistory,
        MsWordDocumentTokenHistory,
        MsExcelDocumentTokenHistory,
        WindowsDirectoryTokenHistory,
        SQLServerTokenHistory,
        KubeconfigTokenHistory,
    ],
    Field(discriminator="token_type"),
]


class TokenAlertDetails(BaseModel):
    # TODO: V2 does not include the 4 in webhook alert data.
    #       Remove defaults we v2 is done.
    channel: str = "DNS"
    token_type: TokenTypes = TokenTypes.DNS
    src_ip: Optional[str] = "127.0.0.1"
    token: str = "default_token_for_v2"

    # Design: Is this a good name? Should it be time of trigger. Or time we recieved the event? Or time we sent this out?
    time: datetime
    memo: Memo
    manage_url: HttpUrl
    # DESIGN/TODO: pin this dict down and make it a type.
    # We know what this can be.
    additional_data: Optional[Dict[str, Any]]

    @validator("time", pre=True)
    def validate_time(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S (UTC)")
        return value

    @property
    def history_url(self):
        return HttpUrl(
            self.manage_url.replace("manage", "history"), scheme=self.manage_url.scheme
        )

    def json_safe_dict(self) -> Dict[str, str]:
        return json_safe_dict(self)

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S (UTC)"),
        }


class SlackField(BaseModel):
    title: str
    value: str
    short: bool = True


class SlackAttachment(BaseModel):
    title: str = "Canarytoken Triggered"
    title_link: HttpUrl
    mrkdwn_in: List[str] = ["title"]
    fallback: str = ""
    fields: List[SlackField]

    def __init__(__pydantic_self__, **data: Any) -> None:
        # HACK: We can do better here.
        data["fallback"] = f"Canarytoken Triggered: {data['title_link']}"
        super().__init__(**data)


class TokenAlertDetailsSlack(BaseModel):
    """Details that are sent to slack webhooks."""

    attachments: List[SlackAttachment]

    def json_safe_dict(self) -> Dict[str, str]:
        return json_safe_dict(self)


class TokenAlertDetailGeneric(TokenAlertDetails):
    ...


class UserName(ConstrainedStr):
    max_lengthint: int = 30
    strip_whitespace: bool = True
    to_lower: bool = False


class User(BaseModel):
    # DESIGN: We need to see how users are handled:
    #         Users hold the `alert_expiry`, `alert_limit`, `alert_count`
    #         Do we want to attach this to the token?
    name: UserName
    email: Optional[EmailStr] = None
    # alert_expiry -> attach this to a user or a token?
    # alert_limit -> attach this to a user or a token?
    # alert_count -> attach this to a user or a token?

    def can_send_alert(self, canarydrop):
        return True  # TODO: user object may need some work.

    def do_accounting(self, canarydrop):
        # TODO: DESIGN: User object how should we manage them
        return


class Anonymous(User):
    name: UserName = UserName("Anonymous")


class DownloadFmtTypes(str, enum.Enum):
    """Enumerates all supported token download format types"""

    ZIP = "zip"
    MSWORD = "msword"
    MSEXCEL = "msexcel"
    PDF = "pdf"
    AWSKEYS = "awskeys"
    KUBECONFIG = "kubeconfig"
    SLACKAPI = "slackapi"
    INCIDENTLISTJSON = "incidentlist_json"
    INCIDENTLISTCSV = "incidentlist_csv"
    MYSQL = "my_sql"
    QRCODE = "qr_code"

    def __str__(self) -> str:
        return str(self.value)


class DownloadContentTypes(str, enum.Enum):
    """Enumerates all supported token download content types"""

    APPZIP = "application/zip"
    APPMSWORD = (
        "application/vnd.openxmlformats-officedocument" + ".wordprocessingml.document"
    )
    APPMSEXCELL = (
        "application/vnd.openxmlformats-officedocument" + ".spreadsheetml.sheet"
    )
    APPPDF = "application/pdf"
    TEXTPLAIN = "text/plain"
    IMAGE = "image/png"

    def __str__(self) -> str:
        return str(self.value)


class TokenDownloadRequest(BaseModel):
    fmt: DownloadFmtTypes
    token: str
    auth: str


class DownloadZipRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.ZIP] = DownloadFmtTypes.ZIP


class DownloadMSWordRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.MSWORD] = DownloadFmtTypes.MSWORD


class DownloadMSExcelRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.MSEXCEL] = DownloadFmtTypes.MSEXCEL


class DownloadPDFRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.PDF] = DownloadFmtTypes.PDF


class DownloadQRCodeRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.QRCODE] = DownloadFmtTypes.QRCODE


class DownloadIncidentListJsonRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.INCIDENTLISTJSON] = DownloadFmtTypes.INCIDENTLISTJSON


class DownloadMySQLRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.MYSQL] = DownloadFmtTypes.MYSQL
    encoded: bool = True


class DownloadIncidentListCSVRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.INCIDENTLISTCSV] = DownloadFmtTypes.INCIDENTLISTCSV


class DownloadAWSKeysRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.AWSKEYS] = DownloadFmtTypes.AWSKEYS


class DownloadKubeconfigRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.KUBECONFIG] = DownloadFmtTypes.KUBECONFIG


class DownloadSplackApiRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.SLACKAPI] = DownloadFmtTypes.SLACKAPI


AnyDownloadRequest = Annotated[
    Union[
        DownloadAWSKeysRequest,
        DownloadIncidentListCSVRequest,
        DownloadIncidentListJsonRequest,
        DownloadKubeconfigRequest,
        DownloadMSExcelRequest,
        DownloadMSWordRequest,
        DownloadMySQLRequest,
        DownloadPDFRequest,
        DownloadSplackApiRequest,
        DownloadZipRequest,
        DownloadQRCodeRequest,
    ],
    Field(discriminator="fmt"),
]


class TokenDownloadResponse(Response):
    contenttype: DownloadContentTypes
    content: Any

    def __init__(__pydantic_self__, **data: Any) -> None:
        file_name = data["filename"]
        content = data["content"]

        headers = {
            "Content-Type": __pydantic_self__.contenttype,
            "Content-Disposition": f"attachment; filename={file_name}",
        }

        super().__init__(content=content, headers=headers)


class DownloadMSWordResponse(TokenDownloadResponse):
    contenttype: Literal[
        DownloadContentTypes.APPMSWORD
    ] = DownloadContentTypes.APPMSWORD
    filename: str
    token: str
    auth: str


class DownloadZipResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.APPZIP] = DownloadContentTypes.APPZIP
    filename: str
    content: bytes
    token: str
    auth: str


class DownloadMSExcelResponse(TokenDownloadResponse):
    contenttype: Literal[
        DownloadContentTypes.APPMSEXCELL
    ] = DownloadContentTypes.APPMSEXCELL
    filename: str
    token: str
    auth: str


class DownloadPDFResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.APPPDF] = DownloadContentTypes.APPPDF
    filename: str
    token: str
    auth: str


class DownloadIncidentListJsonResponse(TokenDownloadResponse):
    contenttype: Literal[
        DownloadContentTypes.TEXTPLAIN
    ] = DownloadContentTypes.TEXTPLAIN
    filename: str
    token: str
    auth: str


class DownloadMySQLResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.APPZIP] = DownloadContentTypes.APPZIP
    filename: str
    token: str
    auth: str


class DownloadQRCodeResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.IMAGE] = DownloadContentTypes.IMAGE
    filename: str
    token: str
    auth: str


class DownloadIncidentListCSVResponse(TokenDownloadResponse):
    contenttype: Literal[
        DownloadContentTypes.TEXTPLAIN
    ] = DownloadContentTypes.TEXTPLAIN
    filename: str
    token: str
    auth: str


class DownloadAWSKeysResponse(TokenDownloadResponse):
    contenttype: Literal[
        DownloadContentTypes.TEXTPLAIN
    ] = DownloadContentTypes.TEXTPLAIN
    filename: str = "credentials"
    token: str
    auth: str
    aws_access_key_id: str
    aws_secret_access_key: str
    region: str
    output: str


class DownloadKubeconfigResponse(TokenDownloadResponse):
    contenttype: Literal[
        DownloadContentTypes.TEXTPLAIN
    ] = DownloadContentTypes.TEXTPLAIN
    filename: str = "kubeconfig"
    token: str
    auth: str


class DownloadSplackApiResponse(TokenDownloadResponse):
    contenttype: Literal[
        DownloadContentTypes.TEXTPLAIN
    ] = DownloadContentTypes.TEXTPLAIN
    slack_api_key: str
    filename: str = "slack_creds"
    token: str
    auth: str


class DownloadGetRequestModel(BaseModel):
    token: str
    auth: str
    fmt: str


class CanarydropSettingsTypes(str, enum.Enum):
    """Enumerates all supported canarydrop settings types"""

    # CLONEDSITESETTING = "clonedsite"
    # SMSSETTING = "sms_enable"
    EMAILSETTING = "email_enable"
    WEBHOOKSETTING = "webhook_enable"
    BROWSERSCANNERSETTING = "browser_scanner_enable"
    WEBIMAGESETTING = "web_image_enable"

    def __str__(self) -> str:
        return str(self.value)


class SettingsRequest(BaseModel):
    # setting: CanarydropSettingsTypes
    value: Literal["on", "off"] = "off"
    token: str = ""
    auth: str = ""


class EmailSettingsRequest(SettingsRequest):
    setting: Literal[
        CanarydropSettingsTypes.EMAILSETTING
    ] = CanarydropSettingsTypes.EMAILSETTING


class WebhookSettingsRequest(SettingsRequest):
    setting: Literal[
        CanarydropSettingsTypes.WEBHOOKSETTING
    ] = CanarydropSettingsTypes.WEBHOOKSETTING


class BrowserScannerSettingsRequest(SettingsRequest):
    setting: Literal[
        CanarydropSettingsTypes.BROWSERSCANNERSETTING
    ] = CanarydropSettingsTypes.BROWSERSCANNERSETTING


class WebImageSettingsRequest(SettingsRequest):
    setting: Literal[
        CanarydropSettingsTypes.WEBIMAGESETTING
    ] = CanarydropSettingsTypes.WEBIMAGESETTING


AnySettingsRequest = Annotated[
    Union[
        EmailSettingsRequest,
        WebhookSettingsRequest,
        BrowserScannerSettingsRequest,
        WebImageSettingsRequest,
    ],
    Field(discriminator="setting"),
]


class SettingsResponse(Response):
    result: Literal["success", "failure"]


class ManageTokenSettingsRequest(BaseModel):
    token: str
    auth: str
    email_enable: Optional[Literal["on", "off"]]
    webhook_enable: Optional[Literal["on", "off"]]
    sms_enable: Optional[Literal["on", "off"]]
    web_image_enable: Optional[Literal["on", "off"]]
    browser_scanner_enable: Optional[Literal["on", "off"]]
    # Add validation for the token and auth fields
