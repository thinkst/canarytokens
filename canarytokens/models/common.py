from __future__ import annotations
from abc import ABCMeta, abstractmethod
import csv
import enum
import re
import sys
from datetime import datetime
from io import BytesIO, StringIO  # noqa: F401
from ipaddress import IPv4Address
from tempfile import SpooledTemporaryFile  # noqa: F401
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
from fastapi.responses import JSONResponse
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConstrainedInt,
    ConstrainedStr,
    EmailStr,
    Field,
    HttpUrl,
    IPvAnyAddress,
    ValidationError,
    root_validator,
    validator,
)
from pydantic.generics import GenericModel
from typing_extensions import Annotated

from canarytokens.constants import (
    CANARYTOKEN_ALPHABET,
    CANARYTOKEN_LENGTH,
    MEMO_MAX_CHARACTERS,
)
from canarytokens.utils import get_src_ip_continent, json_safe_dict, strtobool  # noqa: F401

if sys.version_info >= (3, 11):
    from enum import StrEnum  # Python 3.11+
else:
    from backports.strenum import StrEnum  # Python < 3.11

CANARYTOKEN_RE = re.compile(
    f"[{CANARYTOKEN_ALPHABET}]{{{CANARYTOKEN_LENGTH}}}",
    re.IGNORECASE,
)


def response_error(error, message, status_code=400):
    return JSONResponse(
        {
            "error": str(error),
            "error_message": message,
            "url": "",
            "url_components": None,
            "token": "",
            "email": "",
            "hostname": "",
            "auth": "",
        },
        status_code=status_code,
    )


class Memo(ConstrainedStr):
    max_length: int = MEMO_MAX_CHARACTERS


class Port(ConstrainedInt):
    ge: int = 0
    lt: int = 65535


class Hostname(ConstrainedStr):
    max_length: int = 253
    regex = re.compile(
        r"^(([a-z0-9]|[a-z0-9]?[a-z0-9\-]{1,61}[a-z0-9])\.){1,61}[a-z0-9]{1,61}$",
        re.IGNORECASE,
    )


class Canarytoken(ConstrainedStr):
    max_length: int = CANARYTOKEN_LENGTH
    regex = CANARYTOKEN_RE


class AWSKey(TypedDict):
    access_key_id: str
    secret_access_key: str
    aws_account_id: Optional[str]
    region: str
    output: Literal["json", "yaml", "yaml-stream", "text", "table"]


class CSSClonedSite(TypedDict):
    expected_referrer: str


class AzureID(TypedDict):
    app_id: str
    tenant_id: str
    cert: str
    cert_name: str
    cert_file_name: str


class CrowdStrikeCC(TypedDict):
    token_id: str
    client_id: str
    client_secret: str
    base_url: str


class KubeCerts(TypedDict):
    f: bytes
    c: bytes
    k: bytes


class CreditCard(BaseModel):
    id: str
    number: Optional[str]
    cvc: Optional[str]
    expiration: Optional[str]
    kind: Optional[str]
    name: str
    billing_zip: str
    address: str

    def render_html(self) -> str:
        return f"""<div id=\"cccontainer\"><span id=\"ccname\">{self.name}</span><span id=\"ccnumber\">{self.__format_token()}</span><span id=\"ccexpires\">{self.expiration}</span><span id=\"cccvc\">{self.cvc}</span></div>"""

    def to_csv(self) -> str:
        f = StringIO()
        fn = ["name", "type", "number", "cvc", "exp", "billing_zip"]
        sd = self.to_dict()
        del sd["address"]
        del sd["id"]
        writer = csv.DictWriter(f, fieldnames=fn)
        writer.writeheader()
        writer.writerow(sd)
        return f.getvalue()

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": str(self.id),
            "name": self.name,
            "number": str(self.number),
            "cvc": str(self.cvc),
            "billing_zip": str(self.billing_zip),
            "type": str(self.kind),
            "address": str(self.address),
            "exp": str(self.expiration),
        }

    def __format_token(self):
        if self.kind != "AMEX":
            return " ".join(
                self.number[i : i + 4]  # noqa: E203
                for i in range(0, len(self.number), 4)
            )
        return " ".join([self.number[0:4], self.number[4:10], self.number[10:15]])


class ApiProvider(metaclass=ABCMeta):
    @abstractmethod
    def create_credit_card(
        self,
        token_url: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        address: Optional[str] = None,
        billing_zip: Optional[str] = None,
    ) -> CreditCard:
        pass

    @abstractmethod
    def get_credit_card(self, id: str) -> CreditCard:
        pass

    @abstractmethod
    def get_latest_transaction(self, cc: CreditCard) -> Optional[Dict[str, str]]:
        pass


class TokenTypes(StrEnum):
    WEB = "web"
    DNS = "dns"
    WEB_IMAGE = "web_image"
    MS_WORD = "ms_word"
    MS_EXCEL = "ms_excel"
    ADOBE_PDF = "adobe_pdf"
    WIREGUARD = "wireguard"
    WINDOWS_DIR = "windows_dir"
    WEBDAV = "webdav"
    CLONEDSITE = "clonedsite"
    CSSCLONEDSITE = "cssclonedsite"
    CREDIT_CARD_V2 = "credit_card_v2"
    QR_CODE = "qr_code"
    SVN = "svn"
    SMTP = "smtp"
    SQL_SERVER = "sql_server"
    MY_SQL = "my_sql"
    AWS_KEYS = "aws_keys"
    AZURE_ID = "azure_id"
    SIGNED_EXE = "signed_exe"
    FAST_REDIRECT = "fast_redirect"
    SLOW_REDIRECT = "slow_redirect"
    KUBECONFIG = "kubeconfig"
    LOG4SHELL = "log4shell"
    CMD = "cmd"
    WINDOWS_FAKE_FS = "windows_fake_fs"
    CC = "cc"
    PWA = "pwa"
    IDP_APP = "idp_app"
    SLACK_API = "slack_api"
    LEGACY = "legacy"
    AWS_INFRA = "aws_infra"
    CROWDSTRIKE_CC = "crowdstrike_cc"
    SVG = "svg"

    def __str__(self) -> str:
        return str(self.value)


TOKEN_TYPES_WITH_ARTICLE_AN = [
    TokenTypes.ADOBE_PDF,
    TokenTypes.AWS_KEYS,
    TokenTypes.AWS_INFRA,
    TokenTypes.AZURE_ID,
    TokenTypes.MS_EXCEL,
    TokenTypes.MS_WORD,
    TokenTypes.SQL_SERVER,
    TokenTypes.SVN,
]

READABLE_TOKEN_TYPE_NAMES = {
    TokenTypes.WEB: "Web bug",
    TokenTypes.DNS: "DNS",
    TokenTypes.WEB_IMAGE: "Custom image",
    TokenTypes.MS_WORD: "MS Word",
    TokenTypes.MS_EXCEL: "MS Excel",
    TokenTypes.ADOBE_PDF: "Adobe PDF",
    TokenTypes.WIREGUARD: "WireGuard",
    TokenTypes.WINDOWS_DIR: "Windows folder",
    TokenTypes.WEBDAV: "Network folder",
    TokenTypes.CLONEDSITE: "JS cloned website",
    TokenTypes.CSSCLONEDSITE: "CSS cloned website",
    TokenTypes.QR_CODE: "QR code",
    TokenTypes.SVN: "SVN",
    TokenTypes.SMTP: "Email address",
    TokenTypes.SQL_SERVER: "MS SQL Server",
    TokenTypes.MY_SQL: "MySQL",
    TokenTypes.AWS_KEYS: "AWS key",
    TokenTypes.AZURE_ID: "Azure key",
    TokenTypes.SIGNED_EXE: "Custom EXE / binary",
    TokenTypes.FAST_REDIRECT: "Fast redirect",
    TokenTypes.SLOW_REDIRECT: "Slow redirect",
    TokenTypes.KUBECONFIG: "Kubeconfig",
    TokenTypes.LOG4SHELL: "Log4Shell",
    TokenTypes.CMD: "Sensitive command",
    TokenTypes.WINDOWS_FAKE_FS: "Windows Fake File System",
    TokenTypes.CC: "Credit card",
    TokenTypes.CREDIT_CARD_V2: "Credit card",
    TokenTypes.PWA: "Fake app",
    TokenTypes.SLACK_API: "Slack API",
    TokenTypes.LEGACY: "Legacy",
    TokenTypes.IDP_APP: "SAML2 IdP App",
    TokenTypes.AWS_INFRA: "AWS Infrastructure",
    TokenTypes.CROWDSTRIKE_CC: "CrowdStrike API key",
    TokenTypes.SVG: "SVG",
}

GeneralHistoryTokenType = Literal["blank"]

BlankRequestTokenType = Literal["blank",]

IGNORE_IP_UNSUPPORTED = [TokenTypes.SMTP, TokenTypes.CREDIT_CARD_V2]


class TokenRequest(BaseModel):
    email: Optional[EmailStr]
    webhook_url: Optional[HttpUrl]
    memo: Memo

    def __init__(__pydantic_self__, **data: Any) -> None:
        if data.get("email", False) == "":
            data.pop("email")
        if data.get("webhook_url", False) == "":
            data.pop("webhook_url")
        if isinstance(data.get("token_type", None), str):
            data["token_type"] = TokenTypes(data["token_type"])
        super().__init__(**data)

    @root_validator
    def check_email_or_webhook_opt(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get("webhook_url") and not values.get("email"):
            raise ValueError("either webhook or email is required")
        return values

    def to_dict(self) -> Dict[str, Any]:
        return json_safe_dict(self)

    def json_safe_dict(self) -> Dict[str, str]:
        return json_safe_dict(self)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {TokenTypes: lambda v: v.value}


class TokenEditRequest(BaseModel):
    canarytoken: str
    auth_token: str
    email: Optional[EmailStr]
    webhook_url: Optional[HttpUrl]
    memo: Optional[Memo]


class TokenResponse(BaseModel):
    token: str
    hostname: Hostname
    token_url: Union[HttpUrl, Literal[""], str]
    auth_token: str
    email: Union[EmailStr, Literal[""]] = ""
    webhook_url: Union[HttpUrl, Literal[""]] = ""
    url_components: Optional[List[List[str]]]
    error: Optional[str]
    error_message: Optional[str]
    Url: Union[HttpUrl, Literal[""], None]

    @root_validator(pre=True)
    def normalize_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        for old_key, new_key in [("Auth", "auth_token"), ("Url", "token_url")]:
            if old_key in values and values[old_key] is not None:
                values[new_key] = values.get(old_key)
        return {k.lower(): v for k, v in values.items()}

    def __init__(__pydantic_self__, **data: Any) -> None:
        data["webhook_url"] = data.pop("webhook", "")
        if "token_url" in data:
            data["Url"] = data.get("token_url")
        super().__init__(**data)


class PageRequest(BaseModel):
    token: str
    auth: str


class HistoryPageRequest(PageRequest): ...


class ManagePageRequest(PageRequest): ...


class ASN(BaseModel):
    route: str
    type: str
    asn: str
    domain: str
    name: str


class GeoIPBogonInfo(BaseModel):
    ip: str
    bogon: Literal[True]


class GeoIPInfo(BaseModel):
    # DESIGN/TODO: This is based on 3rd party response. Make all fields optional / match the api we expecting
    loc: Tuple[float, float]  # '-33.9778,18.6167'
    org: Optional[str]  # 'AS29975 Vodacom'
    city: Optional[str]  # 'Cape Town'
    # TODO: Validate country code pycountry?? add a dependency for this??
    country: Optional[str]  # 'ZA',
    region: Optional[str]  # 'Western Cape'
    #  TODO: validate this domain
    hostname: Optional[str]  # 'dnsinfo1-cte-pt.3g.vodacom.co.za
    ip: str  # '41.1.47.253
    timezone: Optional[str]  # 'Africa/Johannesburg
    postal: Optional[str]  # '7100 or EC1A
    asn: Optional[
        ASN
    ]  # {'route': '41.1.0.0/18', 'type': 'isp', 'asn': 'AS29975', 'domain': 'vodacom.com', 'name': 'Vodacom'}
    readme: Optional[str]
    # bogon

    @root_validator(pre=True)
    def validator_bogon(cls, values):
        if values and "bogon" in values:
            raise ValidationError("Bogon implies GeoIPBogonInfo not GeoIPInfo")
        return values

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
        if self.loc:
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
    vendor: Optional[list[str]]
    language: Optional[list[str]]
    enabled: list[str]
    installed: list[str]
    platform: Optional[list[str]]
    version: list[str]
    os: list[str]
    browser: Optional[list[str]]
    r: Optional[list[str]]
    l: Optional[list[str]]


class AWSKeyAdditionalInfo(BaseModel):
    aws_key_log_data: dict[str, list[str]]

    @root_validator(pre=True)
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        keys_to_convert = [
            ("AWS Key Log Data", "aws_key_log_data"),
        ]
        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values:
                values[new_key] = values.pop(old_key)

        return {k.lower(): v for k, v in values.items()}


class AzureIDAdditionalInfo(BaseModel):
    azure_id_log_data: dict[str, list[str]]
    microsoft_azure: dict[str, list[str]]
    location: dict[str, list[str]]
    coordinates: dict[str, list[str]]

    @root_validator(pre=True)
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        keys_to_convert = [
            ("Azure ID Log Data", "azure_id_log_data"),
            ("Microsoft Azure", "microsoft_azure"),
            ("Location", "location"),
            ("Coordinates", "coordinates"),
        ]
        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values:
                values[new_key] = values.pop(old_key)

        return {k.lower(): v for k, v in values.items()}

    def serialize_for_v2(self) -> dict:
        data = self.dict()
        keys_to_convert = [
            ("Azure ID Log Data", "azure_id_log_data"),
            ("Microsoft Azure", "microsoft_azure"),
            ("Location", "location"),
            ("Coordinates", "coordinates"),
        ]
        for value, key in keys_to_convert:
            if key in data:
                data[value] = data.pop(key)
        return data


class CrowdStrikeCCAdditionalInfo(BaseModel):
    crowdstrike_log_data: dict[str, list[str]]

    @root_validator(pre=True)
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        keys_to_convert = [
            ("CrowdStrike Log Data", "crowdstrike_log_data"),
        ]
        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values:
                values[new_key] = values.pop(old_key)

        return {k.lower(): v for k, v in values.items()}

    def serialize_for_v2(self) -> dict:
        data = self.dict()
        keys_to_convert = [
            ("CrowdStrike Log Data", "crowdstrike_log_data"),
        ]
        for value, key in keys_to_convert:
            if key in data:
                data[value] = data.pop(key)
        return data


class AdditionalInfo(BaseModel):
    javascript: Optional[ServiceInfo]
    browser: Optional[BrowserInfo]
    mysql_client: Optional[dict[str, list[str]]]
    r: Optional[list[str]]
    l: Optional[list[str]]
    file_path: Optional[list[str]]

    @root_validator(pre=True)
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        keys_to_convert = [
            ("MySQL Client", "mysql_client"),
        ]

        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values:
                values[new_key] = values.pop(old_key)

        return {k.lower(): v for k, v in values.items()}

    def serialize_for_v2(self) -> dict:
        data = json_safe_dict(self)
        if "browser" in data:
            data["Browser"] = data.pop("browser")
        if "javascript" in data:
            data["Javascript"] = data.pop("javascript")
        if "mysql_client" in data:
            data["MySQL Client"] = data.pop("mysql_client")
        return data


class SMTPHeloField(BaseModel):
    client_name: str
    client_ip: IPv4Address

    class Config:
        json_encoders = {
            IPv4Address: lambda v: str(v),
        }


class SMTPMailField(BaseModel):
    sender: Optional[str]
    recipients: list[str]
    links: list[str]
    headers: list[str]
    helo: SMTPHeloField
    attachments: list[str]

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
        data["recipients"] = [f"<{o}>" for o in data["recipients"]]
        return data


class AlertStatus(enum.StrEnum):
    ALERTABLE = "alertable"
    IGNORED_IP = "ignored_ip"


class TokenHit(BaseModel):
    time_of_hit: float
    src_ip: Optional[str]
    geo_info: Union[GeoIPInfo, GeoIPBogonInfo, None, Literal[""]]
    is_tor_relay: Optional[bool]
    input_channel: str
    src_data: Optional[dict]
    useragent: Optional[str]
    alert_status: AlertStatus = AlertStatus.ALERTABLE

    class Config:
        smart_union = True

    @validator("geo_info", pre=True)
    def adjust_geo_info(cls, value):
        if value == "":
            return None
        return value

    def get_additional_data_for_notification(self) -> Dict[str, Any]:
        additional_data = json_safe_dict(
            self,
            exclude=(
                "time_of_hit",
                "src_ip",
                "is_tor_relay",
                "input_channel",
                "token_type",
                "alert_status",
            ),
        )
        if "additional_data" in additional_data:
            additional_data.update(**additional_data.pop("additional_data"))
        for key, replacement in [("l", "location"), ("r", "referer")]:
            if key in additional_data:
                additional_data[replacement] = additional_data.pop(key)
            if self.src_data and key in self.src_data:
                self.src_data[replacement] = self.src_data[key]

        if additional_data.get("geo_info") is not None:
            continent = get_src_ip_continent(additional_data["geo_info"])
            additional_data["geo_info"]["continent"] = continent

        time = datetime.utcnow()
        additional_data["time_hm"] = time.strftime("%H:%M")
        additional_data["time_ymd"] = time.strftime("%Y/%m/%d")

        return additional_data


class TokenExposedHit(BaseModel):
    time_of_hit: float


TH = TypeVar("TH", bound=TokenHit)


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
            if hit.token_type in {
                TokenTypes.AWS_KEYS,
                TokenTypes.AWS_INFRA,
                TokenTypes.SLACK_API,
                TokenTypes.CREDIT_CARD_V2,
                TokenTypes.CROWDSTRIKE_CC,
            }:
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
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
                ] = hit_data
            else:
                data[f"{hit.time_of_hit:.6f}"] = hit_data
        return data

    def latest_hit(self) -> Optional[TH]:
        if len(self.hits) == 0:
            return None
        return sorted(self.hits, key=lambda o: o.time_of_hit)[-1]


class TokenAlertDetails(BaseModel):
    channel: str = "DNS"
    token_type: TokenTypes = TokenTypes.DNS
    src_ip: Optional[str] = "127.0.0.1"
    src_data: Optional[dict[str, Any]] = None
    token: str = "default_token_for_v2"
    time: datetime
    memo: Memo
    manage_url: AnyHttpUrl
    additional_data: Optional[dict[str, Any]]
    public_domain: Optional[str] = "my.domain"

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


class TokenExposedDetails(BaseModel):
    token_type: TokenTypes
    token: str
    memo: Memo
    key_id: str
    public_location: Optional[str]
    exposed_time: datetime
    manage_url: AnyHttpUrl
    public_domain: Optional[str] = "my.domain"

    @validator("exposed_time", pre=True)
    def validate_time(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S (UTC)")
        return value

    def json_safe_dict(self) -> Dict[str, str]:
        return json_safe_dict(self)

    @property
    def history_url(self):
        return HttpUrl(
            self.manage_url.replace("manage", "history"), scheme=self.manage_url.scheme
        )

    @property
    def time_hm(self) -> str:
        return self.exposed_time.strftime("%H:%M")

    @property
    def time_ymd(self) -> str:
        return self.exposed_time.strftime("%Y/%m/%d")

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S (UTC)"),
        }


class UserName(ConstrainedStr):
    max_lengthint: int = 30
    strip_whitespace: bool = True
    to_lower: bool = False


class User(BaseModel):
    name: UserName
    email: Optional[EmailStr] = None

    def can_send_alert(self, canarydrop):
        return True

    def do_accounting(self, canarydrop):
        return


class Anonymous(User):
    name: UserName = UserName("Anonymous")


class DownloadFmtTypes(StrEnum):
    ZIP = "zip"
    MSWORD = "msword"
    MSEXCEL = "msexcel"
    PDF = "pdf"
    AWSKEYS = "awskeys"
    AZUREIDCONFIG = "azure_id_config"
    AZUREIDCERT = "azure_id"
    KUBECONFIG = "kubeconfig"
    SLACK_API = "slackapi"
    INCIDENTLISTJSON = "incidentlist_json"
    INCIDENTLISTCSV = "incidentlist_csv"
    MYSQL = "my_sql"
    QRCODE = "qr_code"
    CMD = "cmd"
    WINDOWS_FAKE_FS = "windows_fake_fs"
    CC = "cc"
    CSSCLONEDSITE = "cssclonedsite"
    CREDIT_CARD_V2 = "credit_card_v2"
    SVG = "svg"

    def __str__(self) -> str:
        return str(self.value)


class DownloadContentTypes(StrEnum):
    APPZIP = "application/zip"
    APPMSWORD = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    APPMSEXCELL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    APPPDF = "application/pdf"
    TEXTPLAIN = "text/plain"
    IMAGE = "image/png"
    SVG = "image/svg+xml"

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


class DownloadAzureIDConfigRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.AZUREIDCONFIG] = DownloadFmtTypes.AZUREIDCONFIG


class DownloadAzureIDCertRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.AZUREIDCERT] = DownloadFmtTypes.AZUREIDCERT


class DownloadCMDRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.CMD] = DownloadFmtTypes.CMD


class DownloadWindowsFakeFSRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.WINDOWS_FAKE_FS] = DownloadFmtTypes.WINDOWS_FAKE_FS


class DownloadCSSClonedWebRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.CSSCLONEDSITE] = DownloadFmtTypes.CSSCLONEDSITE


class DownloadCCRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.CC] = DownloadFmtTypes.CC


class DownloadKubeconfigRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.KUBECONFIG] = DownloadFmtTypes.KUBECONFIG


class DownloadSlackAPIRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.SLACK_API] = DownloadFmtTypes.SLACK_API


class DownloadCreditCardV2Request(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.CREDIT_CARD_V2] = DownloadFmtTypes.CREDIT_CARD_V2


class DownloadSVGRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.SVG] = DownloadFmtTypes.SVG


AnyDownloadRequest = Annotated[
    Union[
        DownloadAWSKeysRequest,
        DownloadAzureIDConfigRequest,
        DownloadAzureIDCertRequest,
        DownloadCCRequest,
        DownloadCMDRequest,
        DownloadWindowsFakeFSRequest,
        DownloadCSSClonedWebRequest,
        DownloadIncidentListCSVRequest,
        DownloadIncidentListJsonRequest,
        DownloadKubeconfigRequest,
        DownloadMSExcelRequest,
        DownloadMSWordRequest,
        DownloadMySQLRequest,
        DownloadPDFRequest,
        DownloadSlackAPIRequest,
        DownloadZipRequest,
        DownloadQRCodeRequest,
        DownloadCreditCardV2Request,
        DownloadSVGRequest,
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
            "X-Robots-Tag": "noindex",
        }

        super().__init__(content=content, headers=headers)


class DownloadMSWordResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.APPMSWORD] = (
        DownloadContentTypes.APPMSWORD
    )
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
    contenttype: Literal[DownloadContentTypes.APPMSEXCELL] = (
        DownloadContentTypes.APPMSEXCELL
    )
    filename: str
    token: str
    auth: str


class DownloadPDFResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.APPPDF] = DownloadContentTypes.APPPDF
    filename: str
    token: str
    auth: str


class DownloadIncidentListJsonResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
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
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str


class DownloadCCResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str


class DownloadCMDResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str


class DownloadWindowsFakeFSResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str


class DownloadCSSClonedWebResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str


class DownloadAWSKeysResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str = "credentials"
    token: str
    auth: str
    aws_access_key_id: str
    aws_secret_access_key: str
    region: str
    output: str


class DownloadAzureIDConfigResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str


class DownloadAzureIDCertResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str


class DownloadKubeconfigResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str = "kubeconfig"
    token: str
    auth: str


class DownloadSlackAPIResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    slack_api_key: str
    filename: str = "slack_creds"
    token: str
    auth: str


class DownloadCreditCardV2Response(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str = "credit_card"
    token: str
    auth: str


class DownloadSVGResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.SVG] = DownloadContentTypes.SVG
    filename: str
    token: str
    auth: str


class DownloadGetRequestModel(BaseModel):
    token: str
    auth: str
    fmt: str


class FetchLinksRequest(BaseModel):
    email: str
    cf_turnstile_response: str


class CanarydropSettingsTypes(StrEnum):
    EMAILSETTING = "email_enable"
    WEBHOOKSETTING = "webhook_enable"
    BROWSERSCANNERSETTING = "browser_scanner_enable"
    WEBIMAGESETTING = "web_image_enable"
    IPIGNORESETTING = "ip_ignore_enable"


class SettingsRequest(BaseModel):
    value: Literal["on", "off"] = "off"
    token: str = ""
    auth: str = ""


class EmailSettingsRequest(SettingsRequest):
    setting: Literal[CanarydropSettingsTypes.EMAILSETTING] = (
        CanarydropSettingsTypes.EMAILSETTING
    )


class WebhookSettingsRequest(SettingsRequest):
    setting: Literal[CanarydropSettingsTypes.WEBHOOKSETTING] = (
        CanarydropSettingsTypes.WEBHOOKSETTING
    )


class BrowserScannerSettingsRequest(SettingsRequest):
    setting: Literal[CanarydropSettingsTypes.BROWSERSCANNERSETTING] = (
        CanarydropSettingsTypes.BROWSERSCANNERSETTING
    )


class WebImageSettingsRequest(SettingsRequest):
    setting: Literal[CanarydropSettingsTypes.WEBIMAGESETTING] = (
        CanarydropSettingsTypes.WEBIMAGESETTING
    )


class IPIgnoreSettingsRequest(SettingsRequest):
    setting: Literal[CanarydropSettingsTypes.IPIGNORESETTING] = (
        CanarydropSettingsTypes.IPIGNORESETTING
    )


AnySettingsRequest = Annotated[
    Union[
        EmailSettingsRequest,
        WebhookSettingsRequest,
        BrowserScannerSettingsRequest,
        WebImageSettingsRequest,
        IPIgnoreSettingsRequest,
    ],
    Field(discriminator="setting"),
]


class SettingsResponse(BaseModel):
    message: Literal["success", "failure"]


class IPIgnoreListRequest(BaseModel):
    token: str
    auth: str
    ip_ignore_list: List[IPvAnyAddress]


class DeleteResponse(BaseModel):
    message: Literal["success", "failure"]


class EditResponse(BaseModel):
    message: Literal["success", "failure"]


class FetchLinksMessage(StrEnum):
    NOT_CONFIGURED = "failed: cloudflare turnstile not configured"
    TURNSTILE_REQUIRED = "failed: turnstile required"
    INVALID_EMAIL = "failed: invalid email"
    INVALID_TURNSTILE = "failed: invalid turnstile"
    SEND_FAIL = "failed: could not send mail"
    SUCCESS = "success"


class FetchLinksResponse(BaseModel):
    message: FetchLinksMessage


class DefaultResponse(BaseModel):
    result: bool
    message: str = ""


class ManageTokenSettingsRequest(BaseModel):
    token: str
    auth: str
    email_enable: Optional[Literal["on", "off"]]
    webhook_enable: Optional[Literal["on", "off"]]
    sms_enable: Optional[Literal["on", "off"]]
    web_image_enable: Optional[Literal["on", "off"]]
    browser_scanner_enable: Optional[Literal["on", "off"]]


class ManageResponse(BaseModel):
    canarydrop: Dict
    public_ip: Optional[str]
    wg_private_key_seed: Optional[str]
    wg_private_key_n: Optional[str]
    wg_conf: Optional[str]
    wg_qr_code: Optional[str]
    qr_code: Optional[str]
    force_https: Optional[bool]
    clonedsite_js: Optional[str]
    clonedsite_css: Optional[str]
    client_id: Optional[str]
