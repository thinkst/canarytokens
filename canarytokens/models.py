from __future__ import annotations
from abc import ABCMeta, abstractmethod
import csv

import enum
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum  # Python 3.11+
else:
    from backports.strenum import StrEnum  # Python < 3.11
import re
from datetime import datetime
from fastapi.responses import JSONResponse
from io import BytesIO, StringIO
from ipaddress import IPv4Address, IPv6Address
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
    AnyHttpUrl,
    BaseModel,
    ConstrainedInt,
    ConstrainedStr,
    EmailStr,
    Field,
    HttpUrl,
    ValidationError,
    root_validator,
    validator,
    IPvAnyAddress,
)
from pydantic.generics import GenericModel
from typing_extensions import Annotated
from canarytokens.constants import (
    CANARYTOKEN_ALPHABET,
    CANARYTOKEN_LENGTH,
    MEMO_MAX_CHARACTERS,
)
from canarytokens.utils import json_safe_dict, get_src_ip_continent, strtobool

CANARYTOKEN_RE = re.compile(
    f"[{CANARYTOKEN_ALPHABET}]{{{CANARYTOKEN_LENGTH}}}",
    re.IGNORECASE,
)

response_error = lambda error, message, status_code=400: JSONResponse(  # noqa: E731  # lambda is cleaner
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
    # TODO: make enum
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


class KubeCerts(TypedDict):
    """Kube digest (f), cert (c) and key (k) are stored directly and not
    base64 encoded.
    """

    f: bytes  # mTLS digest
    c: bytes  # Cert
    k: bytes  # Key


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
        """Returns an HTML div to render the card info on a website"""
        # return """<div id="cccontainer" style="position: relative; margin: auto; background-image: url('/resources/cc-background-{kind}.png'); height: 290px; width: 460px;"><span id="ccname" style="left: 45px; top: 135px; font-family: 'Open Sans'; position: absolute; font-size: 20pt; color: white;">{name}</span><span id="ccnumber" style="left: 45px; top: 160px; font-family: 'Open Sans'; position: absolute; font-size: 20pt; color: white; word-spacing: .45em;">{number}</span><span id="ccexpires" style="left: 45px; top: 230px; position: absolute; font-family: 'Open Sans'; font-size: 18pt; color: white;">{expiration}</span><span id="cccvc" style="left: 240px; top: 230px; position: absolute; font-family: 'Open Sans'; font-size: 18pt; color: white;">{cvc}</span></div>""".format(
        #     kind=self.kind,
        #     cvc=self.cvc,
        #     number=self.number,
        #     name=self.name,
        #     expiration=self.expiration,
        # )
        return f"""<div id="cccontainer"><span id="ccname">{self.name}</span><span id="ccnumber">{self.__format_token()}</span><span id="ccexpires">{self.expiration}</span><span id="cccvc">{self.cvc}</span></div>"""

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
        """Returns the CC information as a python dict"""
        out = {
            "id": str(self.id),
            "name": self.name,
            "number": str(self.number),
            "cvc": str(self.cvc),
            "billing_zip": str(self.billing_zip),
            "type": str(self.kind),
            "address": str(self.address),
            "exp": str(self.expiration),
        }
        return out

    def __format_token(self):
        digits = 4
        if self.kind != "AMEX":
            split = [
                self.number[i : i + digits]  # noqa: E203
                for i in range(0, len(self.number), digits)
            ]
            return " ".join(split)
        else:
            split = [self.number[0:4], self.number[4:10], self.number[10:15]]
            return " ".join(split)


class ApiProvider(metaclass=ABCMeta):
    """Abstract base class for a credit card API provider"""

    def __init__(self):
        pass

    @abstractmethod
    def create_credit_card(
        self,
        token_url: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        address: Optional[str] = None,
        billing_zip: Optional[str] = None,
    ) -> CreditCard:
        """Abstract method to create a virtual credit card number"""
        pass

    @abstractmethod
    def get_credit_card(self, id: str) -> CreditCard:
        """Abstract method to get a virtual credit card"""
        pass

    @abstractmethod
    def get_latest_transaction(self, cc: CreditCard) -> Optional[Dict[str, str]]:
        """Abstract method to get the latest transaction for a credit card"""
        pass


class TokenTypes(StrEnum):
    """Enumerates all supported token types"""

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
}

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
        if not values.get("webhook_url") and not values.get("email"):
            raise ValueError("either webhook or email is required")
        return values

    # Design: this might be short lived. If not we can do better.
    # Singledispatch if it plays well with pydantic.
    def to_dict(self) -> Dict[str, Any]:
        return json_safe_dict(self)

    def json_safe_dict(self) -> Dict[str, str]:
        return json_safe_dict(self)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {TokenTypes: lambda v: v.value}


class AWSKeyTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS


class AzureIDTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.AZURE_ID] = TokenTypes.AZURE_ID
    azure_id_cert_file_name: str


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
                "webhook_url": "https://slack.com/api/api.test",
            },
        }


class PDFTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF


class CMDTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CMD] = TokenTypes.CMD
    cmd_process: str

    @validator("cmd_process")
    def check_process_name(value: str):
        if not value.endswith(".exe"):
            raise ValueError(f"cmd_process must end in .exe. Given: {value}")
        return value


class WindowsFakeFSTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WINDOWS_FAKE_FS] = TokenTypes.WINDOWS_FAKE_FS
    windows_fake_fs_root: str
    windows_fake_fs_file_structure: str

    @validator("windows_fake_fs_root")
    def check_process_name(value: str):
        _value = value.strip()
        invalid_chars = r'[<>:"/|?*[\]]'
        drive_pattern = r"^[A-Za-z]:[\\/]"

        if not re.match(drive_pattern, _value):
            raise ValueError(
                f"windows_fake_fs_root does not have a drive letter specified. Given: {_value}"
            )
        folder_path = re.sub(drive_pattern, "", _value, 1)
        if re.search(invalid_chars, folder_path):
            raise ValueError(
                f"windows_fake_fs_root contains invalid Windows Path Characters. Given: {_value}"
            )
        if _value.endswith("."):
            raise ValueError(
                f"windows_fake_fs_root cannot end with a fullstop. Given: {_value}"
            )

        return _value


class CCTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CC] = TokenTypes.CC


class PWAType(StrEnum):
    absa = "absa"
    amex = "amex"
    applemail = "applemail"
    applewallet = "applewallet"
    axis = "axis"
    boa = "boa"
    bunq = "bunq"
    capitec = "capitec"
    chase = "chase"
    cred = "cred"
    dashlane = "dashlane"
    discord = "discord"
    facebook = "facebook"
    fnb = "fnb"
    gmail = "gmail"
    googlepay = "googlepay"
    googlewallet = "googlewallet"
    hdfc = "hdfc"
    icici = "icici"
    instagram = "instagram"
    messenger = "messenger"
    monzo = "monzo"
    n26 = "n26"
    nedbank = "nedbank"
    nordpass = "nordpass"
    oldmutual = "oldmutual"
    onepassword = "onepassword"
    paypal = "paypal"
    paytm = "paytm"
    phonepe = "phonepe"
    protonpass = "protonpass"
    rbc = "rbc"
    revolut = "revolut"
    sbi = "sbi"
    signal = "signal"
    snapchat = "snapchat"
    snapscan = "snapscan"
    standard = "standard"
    starling = "starling"
    telegram = "telegram"
    tiktok = "tiktok"
    twitter = "twitter"
    whatsapp = "whatsapp"
    zapper = "zapper"


PWA_APP_TITLES = {
    PWAType.absa: "Absa",
    PWAType.amex: "American Express",
    PWAType.applemail: "Mail",
    PWAType.applewallet: "Wallet",
    PWAType.axis: "Axis Mobile",
    PWAType.boa: "Bank of America",
    PWAType.bunq: "bunq",
    PWAType.capitec: "Capitec",
    PWAType.chase: "Chase",
    PWAType.cred: "CRED",
    PWAType.dashlane: "Dashlane",
    PWAType.discord: "Discord",
    PWAType.facebook: "Facebook",
    PWAType.fnb: "FNB",
    PWAType.gmail: "Gmail",
    PWAType.googlepay: "GPay",
    PWAType.googlewallet: "Wallet",
    PWAType.hdfc: "HDFC Bank",
    PWAType.icici: "iMobile Pay",
    PWAType.instagram: "Instagram",
    PWAType.messenger: "Messenger",
    PWAType.monzo: "Monzo",
    PWAType.n26: "N26",
    PWAType.nedbank: "Nedbank",
    PWAType.nordpass: "NordPass",
    PWAType.oldmutual: "Old Mutual",
    PWAType.onepassword: "1Password",
    PWAType.paypal: "PayPal",
    PWAType.paytm: "Paytm",
    PWAType.phonepe: "PhonePe",
    PWAType.protonpass: "Proton Pass",
    PWAType.rbc: "RBC Mobile",
    PWAType.revolut: "Revolut",
    PWAType.sbi: "YONO SBI",
    PWAType.signal: "Signal",
    PWAType.snapchat: "Snapchat",
    PWAType.snapscan: "SnapScan",
    PWAType.standard: "Standard Bank",
    PWAType.starling: "Starling",
    PWAType.telegram: "Telegram",
    PWAType.tiktok: "TikTok",
    PWAType.twitter: "X",
    PWAType.whatsapp: "WhatsApp",
    PWAType.zapper: "Zapper",
}


class PWATokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.PWA] = TokenTypes.PWA
    icon: PWAType
    app_name: Optional[str]


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

    @classmethod
    def __modify_schema__(cls, field_schema, field):
        field_schema["title"] = "File"


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
    content_type: Literal["image/png", "image/gif", "image/jpeg"]
    filename: str
    file: SpooledTemporaryFile

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

    @classmethod
    def __modify_schema__(cls, field_schema, field):
        field_schema["title"] = "File"


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


class CSSClonedWebTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    expected_referrer: str


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
                "webhook_url": "https://slack.com/api/api.test",
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


class WebDavTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WEBDAV] = TokenTypes.WEBDAV
    webdav_fs_type: str

    @validator("webdav_fs_type")
    def check_webdav_fs_type(value: str):
        from canarytokens.webdav import FsType

        if not value.upper() in FsType.__members__.keys():
            raise ValueError(
                f"webdav_fs_type must be in the FsType enum. Given: {value}"
            )
        return value


class CreditCardV2TokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CREDIT_CARD_V2] = TokenTypes.CREDIT_CARD_V2
    cf_turnstile_response: Optional[str]


class IdPAppType(StrEnum):
    AWS = "aws"
    AZURE = "azure"
    BITWARDEN = "bitwarden"
    DROPBOX = "dropbox"
    DUO = "duo"
    ELASTICSEARCH = "elasticsearch"
    FRESHBOOKS = "freshbooks"
    GCLOUD = "gcloud"
    GDRIVE = "gdrive"
    GITHUB = "github"
    GITLAB = "gitlab"
    GMAIL = "gmail"
    INTUNE = "intune"
    JAMF = "jamf"
    JIRA = "jira"
    KIBANA = "kibana"
    LASTPASS = "lastpass"
    MS365 = "ms365"
    MSTEAMS = "msteams"
    ONEDRIVE = "onedrive"
    ONEPASSWORD = "onepassword"
    OUTLOOK = "outlook"
    PAGERDUTY = "pagerduty"
    SAGE = "sage"
    SALESFORCE = "salesforce"
    SAP = "sap"
    SLACK = "slack"
    VIRTRU = "virtru"
    ZENDESK = "zendesk"
    ZOHO = "zoho"
    ZOOM = "zoom"


IDP_APP_TITLES = {
    IdPAppType.AWS: "AWS",
    IdPAppType.AZURE: "Azure",
    IdPAppType.BITWARDEN: "Bitwarden",
    IdPAppType.DROPBOX: "Dropbox",
    IdPAppType.DUO: "Duo",
    IdPAppType.ELASTICSEARCH: "Elasticsearch",
    IdPAppType.FRESHBOOKS: "Freshbooks",
    IdPAppType.GCLOUD: "Google Cloud",
    IdPAppType.GDRIVE: "Google Drive",
    IdPAppType.GITHUB: "GitHub",
    IdPAppType.GITLAB: "GitLab",
    IdPAppType.GMAIL: "Gmail",
    IdPAppType.INTUNE: "Intune",
    IdPAppType.JAMF: "JAMF",
    IdPAppType.JIRA: "Jira",
    IdPAppType.KIBANA: "Kibana",
    IdPAppType.LASTPASS: "LastPass",
    IdPAppType.MS365: "Microsoft 365",
    IdPAppType.MSTEAMS: "MS Teams",
    IdPAppType.ONEDRIVE: "OneDrive",
    IdPAppType.ONEPASSWORD: "1Password",
    IdPAppType.OUTLOOK: "Outlook",
    IdPAppType.PAGERDUTY: "PagerDuty",
    IdPAppType.SAGE: "Sage",
    IdPAppType.SALESFORCE: "Salesforce",
    IdPAppType.SAP: "SAP",
    IdPAppType.SLACK: "Slack",
    IdPAppType.VIRTRU: "Virtru",
    IdPAppType.ZENDESK: "Zendesk",
    IdPAppType.ZOHO: "Zoho",
    IdPAppType.ZOOM: "Zoom",
}


class IdPAppTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.IDP_APP] = TokenTypes.IDP_APP
    app_type: IdPAppType
    redirect_url: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.IDP_APP,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "redirect_url": "https://youtube.com",
            },
        }


class AWSInfraTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    aws_account_number: str
    aws_region: str


AnyTokenRequest = Annotated[
    Union[
        CCTokenRequest,
        PWATokenRequest,
        CMDTokenRequest,
        WindowsFakeFSTokenRequest,
        FastRedirectTokenRequest,
        QRCodeTokenRequest,
        AWSKeyTokenRequest,
        AzureIDTokenRequest,
        PDFTokenRequest,
        DNSTokenRequest,
        Log4ShellTokenRequest,
        SMTPTokenRequest,
        ClonedWebTokenRequest,
        CSSClonedWebTokenRequest,
        WindowsDirectoryTokenRequest,
        WebDavTokenRequest,
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
        CreditCardV2TokenRequest,
        IdPAppTokenRequest,
        AWSInfraTokenRequest,
    ],
    Field(discriminator="token_type"),
]


class TokenEditRequest(BaseModel):
    canarytoken: str
    auth_token: str
    email: Optional[EmailStr]
    webhook_url: Optional[HttpUrl]
    memo: Optional[Memo]


class AWSInfraTokenEditRequest(TokenEditRequest):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    aws_account_number: Optional[str]
    aws_region: Optional[str]


AnyTokenEditRequest = Annotated[
    Union[AWSInfraTokenEditRequest], Field(discriminator="token_type")
]


class TokenResponse(BaseModel):
    # token_type: Literal["blank"] = "blank"
    token: str
    # TODO: make host name validation stricter
    hostname: Hostname
    # `str` for token_url is needed for local dev
    token_url: Union[HttpUrl, Literal[""], str]
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
    def normalize_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        keys_to_convert = [
            # TODO: make is consistent.
            ("Auth", "auth_token"),
            ("Url", "token_url"),
        ]

        for old_key, new_key in keys_to_convert:  # pragma: no cover
            if old_key in values and values[old_key] is not None:
                values[new_key] = values.get(old_key)

        return {k.lower(): v for k, v in values.items()}

    def __init__(__pydantic_self__, **data: Any) -> None:
        data["webhook_url"] = data.pop("webhook", "")
        if "token_url" in data:
            data["Url"] = data.get("token_url")

        super().__init__(**data)


class AWSKeyTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    output: str


class AzureIDTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.AZURE_ID] = TokenTypes.AZURE_ID
    app_id: str
    tenant_id: str
    cert: str
    cert_name: str
    cert_file_name: str


class PDFTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF
    hostname: str  # Hostname Local testing fails this check TODO: FIXME


class CMDTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CMD] = TokenTypes.CMD
    reg_file: str


class WindowsFakeFSTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WINDOWS_FAKE_FS] = TokenTypes.WINDOWS_FAKE_FS
    powershell_file: str


class CCTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CC] = TokenTypes.CC
    kind: str
    number: str
    cvc: str
    expiration: str
    name: str
    billing_zip: str
    rendered_html: str


class PWATokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.PWA] = TokenTypes.PWA
    pwa_icon: str
    pwa_app_name: str


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
                "webhook_url": "https://slack.com/api/api.test",
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
        if "Url" in data and data["Url"]:  # pragma: no cover
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
    sql_server_sql_action: Optional[Literal["INSERT", "DELETE", "UPDATE", "SELECT"]]
    sql_server_table_name: Optional[str]
    sql_server_view_name: Optional[str]
    sql_server_function_name: Optional[str]
    sql_server_trigger_name: Optional[str]


class ClonedWebTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    clonedsite_js: Optional[str]


class CSSClonedWebTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    css: Optional[str]
    client_id: Optional[str]


class FastRedirectTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.DNS,
                "memo": "Reminder note when this token is triggered",
                "email": "username@domain.com",
                "webhook_url": "https://slack.com/api/api.test",
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
    def set_token_usage_info(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        values["token_with_usage_info"] = (
            f"{cls._hostname_marker}{{hostname}}.{cls._token_marker}.{values['hostname']}"
        )
        return values

    @root_validator(pre=True)
    def set_token_usage(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        values["token_usage"] = (
            f"${{jndi:ldap://{cls._hostname_marker}${{hostName}}.{cls._token_marker}.{values['hostname']}/a}}"
        )
        return values

    class Config:
        schema_extra = {
            "example": {
                "token_type": TokenTypes.LOG4SHELL,
                "memo": "Added to user login portal.",
                "email": "username@domain.com",
                "webhook_url": "https://slack.com/api/api.test",
            },
        }


class WindowsDirectoryTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR


class WebDavTokenResponse(TokenResponse):
    webdav_fs_type: str
    token_type: Literal[TokenTypes.WEBDAV] = TokenTypes.WEBDAV
    webdav_password: str
    webdav_server: str


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


class CreditCardV2TokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CREDIT_CARD_V2] = TokenTypes.CREDIT_CARD_V2
    card_id: str
    name_on_card: str
    card_number: str
    cvv: str
    expiry_month: int
    expiry_year: int


class IdPAppTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.IDP_APP] = TokenTypes.IDP_APP
    entity_id: str
    app_type: IdPAppType


class AWSInfraTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    aws_region: str
    aws_account_number: str
    tf_module_prefix: str
    ingesting: bool  # TODO: remove


AnyTokenResponse = Annotated[
    Union[
        CCTokenResponse,
        PWATokenResponse,
        CMDTokenResponse,
        WindowsFakeFSTokenResponse,
        CustomImageTokenResponse,
        SMTPTokenResponse,
        SvnTokenResponse,
        CustomBinaryTokenResponse,
        SlowRedirectTokenResponse,
        AWSKeyTokenResponse,
        AzureIDTokenResponse,
        MsWordDocumentTokenResponse,
        Log4ShellTokenResponse,
        MsExcelDocumentTokenResponse,
        QRCodeTokenResponse,
        PDFTokenResponse,
        DNSTokenResponse,
        MySQLTokenResponse,
        WireguardTokenResponse,
        WindowsDirectoryTokenResponse,
        WebDavTokenResponse,
        FastRedirectTokenResponse,
        ClonedWebTokenResponse,
        CSSClonedWebTokenResponse,
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
        CreditCardV2TokenResponse,
        IdPAppTokenResponse,
        AWSInfraTokenResponse,
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
            # TODO: make this consistent.
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
            # TODO: make this consistent.
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
        """Serialize an `AzureIDTokenHit` into a dict
        that holds the equivalent info in the v2 shape.
        Returns:
            dict: AzureIDTokenHit in v2 dict representation.
        """
        data = self.dict()
        keys_to_convert = [
            # TODO: make this consistent.
            ("Azure ID Log Data", "azure_id_log_data"),
            ("Microsoft Azure", "microsoft_azure"),
            ("Location", "location"),
            ("Coordinates", "coordinates"),
        ]
        for value, key in keys_to_convert:
            if key in data:
                data[value] = data.pop(key)
        return data


class AdditionalInfo(BaseModel):
    # the ServiceInfo keys are dynamic
    # this only works for our test
    javascript: Optional[ServiceInfo]
    browser: Optional[BrowserInfo]
    # TODO: split this off - additional info can be handled separately.
    #       See `AWSKeyAdditionalInfo`
    mysql_client: Optional[dict[str, list[str]]]
    r: Optional[list[str]]
    l: Optional[list[str]]
    file_path: Optional[list[str]]

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
    def normalize_additional_info_names(cls, values: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        keys_to_convert = [
            # TODO: make this consistent.
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
        # V2 Compatible serialization
        data["recipients"] = [f"<{o}>" for o in data["recipients"]]
        return data


class AlertStatus(enum.StrEnum):
    ALERTABLE = "alertable"
    IGNORED_IP = "ignored_ip"
    # add other ignore reasons as needed


class TokenHit(BaseModel):
    # token_type: GeneralHistoryTokenType
    time_of_hit: float
    src_ip: Optional[str]
    geo_info: Union[GeoIPInfo, GeoIPBogonInfo, None, Literal[""]]
    is_tor_relay: Optional[bool]
    input_channel: str
    src_data: Optional[dict]  # v2 stores empty {} src_data for tokens without src_data.
    useragent: Optional[str]
    alert_status: AlertStatus = AlertStatus.ALERTABLE

    class Config:
        smart_union = True

    @validator("geo_info", pre=True)
    def adjust_geo_info(cls, value):
        # Allow loading v2 data.
        if value == "":
            return None
        return value

    def get_additional_data_for_notification(self) -> Dict[str, Any]:
        """
        Some tokens have additional info that should be included
        in webhook notifications. The dict returned from this function
        is included in webhook outputs.

        Returns:
            Dict[str, str]: Key value pairs to include in webhook info.
        """

        additional_data = json_safe_dict(
            self,
            exclude=(
                "time_of_hit",
                "src_ip",
                "is_tor_relay",
                "input_channel",
                "token_type",
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


class AzureIDTokenHit(TokenHit):
    token_type: Literal[TokenTypes.AZURE_ID] = TokenTypes.AZURE_ID
    additional_info: Optional[AzureIDAdditionalInfo]

    class Config:
        allow_population_by_field_name = True

    def serialize_for_v2(self) -> dict:
        """Serialize an `AzureIDTokenHit` into a dict
        that holds the equivalent info in the v2 shape.
        Returns:
            dict: AzureIDTokenHit in v2 dict representation.
        """
        data = json_safe_dict(self, exclude=("token_type", "time_of_hit"))
        if "additional_info" in data:
            data["additional_info"] = self.additional_info.serialize_for_v2()
        return data


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

    @property
    def service_used(self):
        if self.additional_info is None:
            return False
        if service_used := self.additional_info.aws_key_log_data.get(
            "service_used", False
        ):
            if isinstance(service_used, list):
                return service_used[0]
            else:
                return service_used
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
            log_data.update(
                {
                    "safety_net": [str(data["safety_net"])],
                    "service_used": [str(data["service_used"])],
                }
            )
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


class TokenExposedHit(BaseModel):
    time_of_hit: float


class AWSKeyTokenExposedHit(TokenExposedHit):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    public_location: Optional[str]
    input_channel: str = "HTTP"


class SlackAPITokenHit(TokenHit):
    token_type: Literal[TokenTypes.SLACK_API] = TokenTypes.SLACK_API
    additional_info: Optional[dict]

    def serialize_for_v2(self) -> dict:
        """Serialize an `AWSKeyTokenHit` into a dict
        that holds the equivalent info in the v2 shape.
        Returns:
            dict: AWSKeyTokenHit in v2 dict representation.
        """
        data = json_safe_dict(self, exclude=("token_type", "time_of_hit"))
        if "user_agent" in data:
            data["useragent"] = data.pop("user_agent")
        return data


class DNSTokenHit(TokenHit):
    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS


class CSSClonedWebTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    referrer: Optional[str]


class PDFTokenHit(TokenHit):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF


class CCTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CC] = TokenTypes.CC
    last4: Optional[str]
    amount: Optional[str]
    merchant: Optional[str]


class GeolocationCoordinates(BaseModel):
    accuracy: Optional[float]
    altitude: Optional[float]
    altitudeAccuracy: Optional[float]
    heading: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    speed: Optional[float]


class GeolocationPosition(BaseModel):
    coords: Optional[GeolocationCoordinates]
    timestamp: Optional[int]


class PWATokenHit(TokenHit):
    token_type: Literal[TokenTypes.PWA] = TokenTypes.PWA
    location: Optional[GeolocationPosition]


class CMDTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CMD] = TokenTypes.CMD


class WindowsFakeFSTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WINDOWS_FAKE_FS] = TokenTypes.WINDOWS_FAKE_FS


class SMTPTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    mail: Optional[SMTPMailField]


class KubeconfigTokenHit(TokenHit):
    token_type: Literal[TokenTypes.KUBECONFIG] = TokenTypes.KUBECONFIG
    location: str


class MsWordDocumentTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD


class WindowsDirectoryTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WINDOWS_DIR] = TokenTypes.WINDOWS_DIR
    src_data: Optional[dict]


class WebDavAdditionalInfo(BaseModel):
    file_path: Optional[str]
    useragent: Optional[str]

    def serialize_for_v2(self) -> dict:
        return self.dict()


class WebDavTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WEBDAV] = TokenTypes.WEBDAV
    additional_info: Optional[WebDavAdditionalInfo]


class MsExcelDocumentTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MS_EXCEL] = TokenTypes.MS_EXCEL


class SvnTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SVN] = TokenTypes.SVN


class SQLServerTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER


class WebBugTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB
    request_headers: Optional[dict]
    request_args: Optional[dict]
    additional_info: AdditionalInfo = AdditionalInfo()

    class Config:
        allow_population_by_field_name = True


class CustomImageTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WEB_IMAGE] = TokenTypes.WEB_IMAGE
    additional_info: AdditionalInfo = AdditionalInfo()


class ClonedWebTokenHit(TokenHit):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    # TODO fix API spelling to 'referrer' (comes from JS document.referrer)
    referer: Optional[Union[str, bytes]]
    location: Optional[Union[str, bytes]]


class SlowRedirectTokenHit(TokenHit):
    token_type: Literal[TokenTypes.SLOW_REDIRECT] = TokenTypes.SLOW_REDIRECT
    referer: Optional[Union[str, bytes]]
    location: Optional[Union[str, bytes]]
    additional_info: AdditionalInfo = AdditionalInfo()


class FastRedirectTokenHit(TokenHit):
    token_type: Literal[TokenTypes.FAST_REDIRECT] = TokenTypes.FAST_REDIRECT
    referer: Optional[Union[str, bytes]]
    location: Optional[Union[str, bytes]]
    additional_info: AdditionalInfo = AdditionalInfo()


class Log4ShellTokenHit(TokenHit):
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL
    src_data: Optional[dict]


class QRCodeTokenHit(TokenHit):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE


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


class CreditCardV2AdditionalInfo(BaseModel):
    merchant: Optional[str]
    merchant_identifier: Optional[str]
    transaction_amount: Optional[str]
    transaction_currency: Optional[str]
    masked_card_number: Optional[str]
    transaction_date: Optional[str]
    transaction_type: Optional[str]
    status: Optional[str]


class CreditCardV2TokenHit(TokenHit):
    token_type: Literal[TokenTypes.CREDIT_CARD_V2] = TokenTypes.CREDIT_CARD_V2
    additional_info: Optional[CreditCardV2AdditionalInfo]

    def serialize_for_v2(self) -> dict:
        """Serialize an `CreditCardV2TokenHit` into a dict
        that holds the equivalent info in the v2 shape.
        Returns:
            dict: CreditCardV2TokenHit in v2 dict representation.
        """
        return json_safe_dict(self, exclude=("token_type", "time_of_hit"))


class LegacyTokenHit(TokenHit):
    # excel; word; image; QR;
    token_type: Literal[TokenTypes.LEGACY] = TokenTypes.LEGACY
    # zip;
    src_data: Optional[dict]
    # web
    request_headers: Optional[dict]
    request_args: Optional[dict]
    # web; image
    additional_info: Optional[AdditionalInfo] = AdditionalInfo()
    # cloned_web
    referer: Optional[Union[str, bytes]]
    location: Optional[Union[str, bytes]]
    # smtp
    mail: Optional[SMTPMailField]


class IdPAppTokenHit(TokenHit):
    token_type: Literal[TokenTypes.IDP_APP] = TokenTypes.IDP_APP
    additional_info: AdditionalInfo = AdditionalInfo()


class AwsInfraAdditionalInfo(BaseModel):
    event: Optional[dict[str, Any]]
    decoy_resource: Optional[dict[str, Any]]
    identity: Optional[dict[str, Any]]
    metadata: Optional[dict[str, Any]]

    def serialize_for_v2(self) -> dict:
        return self.dict()


class AWSInfraTokenHit(TokenHit):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    input_channel: str = "HTTP"
    additional_info: Optional[AwsInfraAdditionalInfo]

    def serialize_for_v2(self) -> dict:
        return json_safe_dict(self, exclude=("token_type", "time_of_hit"))


AnyTokenHit = Annotated[
    Union[
        CCTokenHit,
        PWATokenHit,
        CMDTokenHit,
        WindowsFakeFSTokenHit,
        DNSTokenHit,
        AWSKeyTokenHit,
        AzureIDTokenHit,
        SlackAPITokenHit,
        PDFTokenHit,
        ClonedWebTokenHit,
        CSSClonedWebTokenHit,
        Log4ShellTokenHit,
        SlowRedirectTokenHit,
        FastRedirectTokenHit,
        SMTPTokenHit,
        WebBugTokenHit,
        WebDavTokenHit,
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
        LegacyTokenHit,
        CreditCardV2TokenHit,
        IdPAppTokenHit,
        AWSInfraTokenHit,
    ],
    Field(discriminator="token_type"),
]

AnyTokenExposedHit = AWSKeyTokenExposedHit

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
            if (
                isinstance(hit, AWSKeyTokenHit)
                or isinstance(hit, AWSInfraTokenHit)
                or isinstance(hit, SlackAPITokenHit)
                or isinstance(hit, CreditCardV2TokenHit)
            ):
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


class AWSKeyTokenHistory(TokenHistory[AWSKeyTokenHit]):
    token_type: Literal[TokenTypes.AWS_KEYS] = TokenTypes.AWS_KEYS
    hits: List[AWSKeyTokenHit]


class AzureIDTokenHistory(TokenHistory):
    token_type: Literal[TokenTypes.AZURE_ID] = TokenTypes.AZURE_ID
    hits: List[AzureIDTokenHit]


class SlackAPITokenHistory(TokenHistory[SlackAPITokenHit]):
    token_type: Literal[TokenTypes.SLACK_API] = TokenTypes.SLACK_API
    hits: List[SlackAPITokenHit] = []


class DNSTokenHistory(TokenHistory[DNSTokenHit]):
    token_type: Literal[TokenTypes.DNS] = TokenTypes.DNS
    hits: List[DNSTokenHit]


class PDFTokenHistory(TokenHistory[PDFTokenHit]):
    token_type: Literal[TokenTypes.ADOBE_PDF] = TokenTypes.ADOBE_PDF
    hits: List[PDFTokenHit]


class CCTokenHistory(TokenHistory[CCTokenHit]):
    token_type: Literal[TokenTypes.CC] = TokenTypes.CC
    hits: List[CCTokenHit]


class PWATokenHistory(TokenHistory[PWATokenHit]):
    token_type: Literal[TokenTypes.PWA] = TokenTypes.PWA
    hits: List[PWATokenHit]


class CMDTokenHistory(TokenHistory[CMDTokenHit]):
    token_type: Literal[TokenTypes.CMD] = TokenTypes.CMD
    hits: List[CMDTokenHit]


class WindowsFakeFSTokenHistory(TokenHistory[WindowsFakeFSTokenHit]):
    token_type: Literal[TokenTypes.WINDOWS_FAKE_FS] = TokenTypes.WINDOWS_FAKE_FS
    hits: List[WindowsFakeFSTokenHit]


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


class WebDavTokenHistory(TokenHistory[WebDavTokenHit]):
    token_type: Literal[TokenTypes.WEBDAV] = TokenTypes.WEBDAV
    hits: List[WebDavTokenHit] = []


class CustomBinaryTokenHistory(TokenHistory[CustomBinaryTokenHit]):
    token_type: Literal[TokenTypes.SIGNED_EXE] = TokenTypes.SIGNED_EXE
    hits: List[CustomBinaryTokenHit] = []


class SQLServerTokenHistory(TokenHistory[SQLServerTokenHit]):
    token_type: Literal[TokenTypes.SQL_SERVER] = TokenTypes.SQL_SERVER
    hits: List[SQLServerTokenHit]


class WebBugTokenHistory(TokenHistory[WebBugTokenHit]):
    token_type: Literal[TokenTypes.WEB] = TokenTypes.WEB
    hits: List[WebBugTokenHit] = []


class ClonedWebTokenHistory(TokenHistory[ClonedWebTokenHit]):
    token_type: Literal[TokenTypes.CLONEDSITE] = TokenTypes.CLONEDSITE
    hits: List[ClonedWebTokenHit] = []


class CSSClonedWebTokenHistory(TokenHistory[CSSClonedWebTokenHit]):
    token_type: Literal[TokenTypes.CSSCLONEDSITE] = TokenTypes.CSSCLONEDSITE
    hits: List[CSSClonedWebTokenHit] = []


class Log4ShellTokenHistory(TokenHistory[Log4ShellTokenHit]):
    token_type: Literal[TokenTypes.LOG4SHELL] = TokenTypes.LOG4SHELL
    hits: List[Log4ShellTokenHit] = []


class QRCodeTokenHistory(TokenHistory[QRCodeTokenHit]):
    token_type: Literal[TokenTypes.QR_CODE] = TokenTypes.QR_CODE


class SMTPTokenHistory(TokenHistory[SMTPTokenHit]):
    token_type: Literal[TokenTypes.SMTP] = TokenTypes.SMTP
    hits: List[SMTPTokenHit] = []


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


class CreditCardV2TokenHistory(TokenHistory[CreditCardV2TokenHit]):
    token_type: Literal[TokenTypes.CREDIT_CARD_V2] = TokenTypes.CREDIT_CARD_V2
    hits: List[CreditCardV2TokenHit] = []


class LegacyTokenHistory(TokenHistory[LegacyTokenHit]):
    token_type: Literal[TokenTypes.LEGACY] = TokenTypes.LEGACY
    hits: List[LegacyTokenHit] = []


class IdPAppTokenHistory(TokenHistory[IdPAppTokenHit]):
    token_type: Literal[TokenTypes.IDP_APP] = TokenTypes.IDP_APP
    hits: List[IdPAppTokenHit] = []


class AWSInfraTokenHistory(TokenHistory[AWSInfraTokenHit]):
    token_type: Literal[TokenTypes.AWS_INFRA] = TokenTypes.AWS_INFRA
    hits: List[AWSInfraTokenHit] = []


# AnyTokenHistory is used to type annotate functions that
# handle any token history. It makes use of an annotated type
# that discriminates on `token_type` so pydantic can parse
# TokenHistory where they differ only in `token_type`.
AnyTokenHistory = Annotated[
    Union[
        CCTokenHistory,
        PWATokenHistory,
        CMDTokenHistory,
        WindowsFakeFSTokenHistory,
        DNSTokenHistory,
        AWSKeyTokenHistory,
        AzureIDTokenHistory,
        SlackAPITokenHistory,
        PDFTokenHistory,
        SMTPTokenHistory,
        ClonedWebTokenHistory,
        CSSClonedWebTokenHistory,
        Log4ShellTokenHistory,
        SlowRedirectTokenHistory,
        FastRedirectTokenHistory,
        WebBugTokenHistory,
        WebDavTokenHistory,
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
        LegacyTokenHistory,
        CreditCardV2TokenHistory,
        IdPAppTokenHistory,
        AWSInfraTokenHistory,
    ],
    Field(discriminator="token_type"),
]


class TokenAlertDetails(BaseModel):
    # TODO: V2 does not include the 4 in webhook alert data.
    #       Remove defaults we v2 is done.
    channel: str = "DNS"
    token_type: TokenTypes = TokenTypes.DNS
    src_ip: Optional[str] = "127.0.0.1"
    src_data: Optional[dict[str, Any]] = None
    token: str = "default_token_for_v2"

    # Design: Is this a good name? Should it be time of trigger. Or time we received the event? Or time we sent this out?
    time: datetime
    memo: Memo
    manage_url: AnyHttpUrl
    # DESIGN/TODO: pin this dict down and make it a type.
    # We know what this can be.
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
    # for backwards compatibility only
    # use can_send_alert() and do_accounting() from queries.py instead
    # DESIGN: We need to see how users are handled:
    #         Users hold the `alert_expiry`, `alert_limit`, `alert_count`
    #         Do we want to attach this to the token?
    name: UserName
    email: Optional[EmailStr] = None

    def can_send_alert(self, canarydrop):
        return True  # TODO: user object may need some work.

    def do_accounting(self, canarydrop):
        # TODO: DESIGN: User object how should we manage them
        return


class Anonymous(User):
    name: UserName = UserName("Anonymous")


class DownloadFmtTypes(StrEnum):
    """Enumerates all supported token download format types"""

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

    def __str__(self) -> str:
        return str(self.value)


class DownloadContentTypes(StrEnum):
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
    ...


class DownloadAzureIDCertResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str
    token: str
    auth: str
    ...


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


class DownloadGetRequestModel(BaseModel):
    token: str
    auth: str
    fmt: str


class FetchLinksRequest(BaseModel):
    email: str
    cf_turnstile_response: str


class CanarydropSettingsTypes(StrEnum):
    """Enumerates all supported canarydrop settings types"""

    # CLONEDSITESETTING = "clonedsite"
    # SMSSETTING = "sms_enable"
    EMAILSETTING = "email_enable"
    WEBHOOKSETTING = "webhook_enable"
    BROWSERSCANNERSETTING = "browser_scanner_enable"
    WEBIMAGESETTING = "web_image_enable"
    IPIGNORESETTING = "ip_ignore_enable"

    def __str__(self) -> str:
        return str(self.value)


class SettingsRequest(BaseModel):
    # setting: CanarydropSettingsTypes
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

    @validator("ip_ignore_list", each_item=True)
    def only_ipv4(cls, v):
        if isinstance(v, IPv6Address):
            raise ValueError("IPv6 addresses are not supported.")
        return v


class IPIgnoreListResponse(BaseModel):
    ip_ignore_list: List[str]


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


class ManageTokenSettingsRequest(BaseModel):
    token: str
    auth: str
    email_enable: Optional[Literal["on", "off"]]
    webhook_enable: Optional[Literal["on", "off"]]
    sms_enable: Optional[Literal["on", "off"]]
    web_image_enable: Optional[Literal["on", "off"]]
    browser_scanner_enable: Optional[Literal["on", "off"]]
    # Add validation for the token and auth fields


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


class HistoryResponse(BaseModel):
    canarydrop: Dict
    history: AnyTokenHistory
    google_api_key: Optional[str]


class AWSInfraAssetType(StrEnum):
    S3_BUCKET = "S3Bucket"
    SQS_QUEUE = "SQSQueue"
    SSM_PARAMETER = "SSMParameter"
    SECRETS_MANAGER_SECRET = "SecretsManagerSecret"
    DYNAMO_DB_TABLE = "DynamoDBTable"


class AWSInfraAssetField(StrEnum):
    BUCKET_NAME = "bucket_name"
    OBJECTS = "objects"
    SQS_QUEUE_NAME = "sqs_queue_name"
    SSM_PARAMETER_NAME = "ssm_parameter_name"
    SECRET_NAME = "secret_name"
    TABLE_NAME = "table_name"
    TABLE_ITEMS = "table_items"


class AWSInfraConfigStartRequest(BaseModel):
    canarytoken: str
    auth_token: str


class AWSInfraConfigStartResponse(BaseModel):
    result: bool
    message: str = ""
    role_setup_commands: dict


class AWSInfraTriggerOperationRequest(BaseModel):  # before handle id created
    canarytoken: str
    auth_token: str
    external_id: Optional[str] = None


class AWSInfraHandleRequest(BaseModel):
    handle: str


class AWSInfraHandleResponse(BaseModel):  # before response received
    handle: str
    message: str = ""
    error: str = ""


class AWSInfraCheckRoleReceivedResponse(BaseModel):
    result: bool
    message: str = ""
    handle: str
    session_credentials_retrieved: bool
    error: str = ""


class AWSInfraInventoryCustomerAccountReceivedResponse(BaseModel):
    result: bool
    message: str = ""
    handle: str
    proposed_plan: dict = {}
    error: str = ""
    data_generation_remaining: int = 0


class AWSInfraGenerateDataChoiceRequest(BaseModel):
    canarytoken: str
    auth_token: str
    asset_type: AWSInfraAssetType
    asset_field: AWSInfraAssetField
    parent_asset_name: Optional[str] = None
    plan: Optional[dict] = None


class AWSInfraGenerateDataChoiceResponse(BaseModel):
    result: bool
    message: str = ""
    proposed_data: Optional[str] = None
    data_generation_remaining: int = 0


class AWSInfraSavePlanRequest(BaseModel):
    canarytoken: str
    auth_token: str
    plan: Any


class AWSInfraSavePlanResponse(BaseModel):
    result: bool
    message: str = ""
    terraform_module_source: str = ""


class DefaultResponse(BaseModel):
    result: bool
    message: str = ""


class AWSInfraSetupIngestionReceivedResponse(BaseModel):
    result: bool
    message: str = ""
    handle: str
    terraform_module_snippet: Optional[dict] = None
    role_cleanup_commands: Optional[dict] = None
    error: str = ""


class AWSInfraTeardownReceivedResponse(BaseModel):
    result: bool
    message: str = ""
    handle: str
    role_cleanup_commands: Optional[dict] = None
    error: str = ""


class AWSInfraOperationType(StrEnum):
    CHECK_ROLE = "Check-Role"
    INVENTORY = "Inventory"
    SETUP_INGESTION = "Setup-Ingestion"
    PROVISION_INGESTION_BUS = "Provision-Ingestion-Bus"
    TEARDOWN = "Teardown"


class AWSInfraManagementResponseRequest(BaseModel):
    handle: str
    operation: AWSInfraOperationType
    result: dict


class AWSInfraGenerateChildAssetsRequest(BaseModel):
    canarytoken: str
    auth_token: str
    assets: dict[
        Union[
            Literal[AWSInfraAssetType.S3_BUCKET],
            Literal[AWSInfraAssetType.DYNAMO_DB_TABLE],
        ],
        list[str],
    ]


class AWSInfraGenerateChildAssetsResponse(BaseModel):
    assets: dict[
        Union[
            Literal[AWSInfraAssetType.S3_BUCKET],
            Literal[AWSInfraAssetType.DYNAMO_DB_TABLE],
        ],
        dict[str, list[str]],
    ]
    data_generation_remaining: int = 0


class AWSInfraState(enum.Flag):
    # Base states
    INITIAL = enum.auto()  # initial state, before any operation
    CHECK_ROLE = enum.auto()  # after config started
    INVENTORY = enum.auto()  # after check-role succeeded
    GENERATE_CHILD_ASSETS = enum.auto()  # after inventorying
    PLAN = enum.auto()  # after inventorying
    SETUP_INGESTION = enum.auto()  # after plan saved

    # Overlay states
    INGESTING = enum.auto()
    SUCCEEDED = enum.auto()


class AWSInfraServiceError(StrEnum):
    FAILURE_CHECK_ROLE = "FAILURE_CHECK_ROLE"
    FAILURE_INGESTION_BUS_IS_FULL = "FAILURE_INGESTION_BUS_IS_FULL"
    FAILURE_INGESTION_BUS_PROVISION = "FAILURE_INGESTION_BUS_PROVISION"
    FAILURE_INGESTION_SETUP = "FAILURE_INGESTION_SETUP"
    FAILURE_INGESTION_TEARDOWN = "FAILURE_INGESTION_TEARDOWN"
    FAILURE_INVENTORY = "FAILURE_INVENTORY"
    FAILURE_MGMT_RESPONSE = "FAILURE_MGMT_RESPONSE"
    FAILURE_TRIG_ALERT = "FAILURE_TRIG_ALERT"
    FAILURE_INVENTORY_REGION_DISABLED = "FAILURE_INVENTORY_REGION_DISABLED"
    FAILURE_INVENTORY_ACCESS_DENIED = "FAILURE_INVENTORY_ACCESS_DENIED"
    FAILURE_INVENTORY_TOKEN_EXISTS = "FAILURE_INVENTORY_TOKEN_EXISTS"
    OP_MISSING_KEY = "OP_MISSING_KEY"
    REQ_HANDLE_INVALID = "REQ_HANDLE_INVALID"
    REQ_HANDLE_TIMEOUT = "REQ_HANDLE_TIMEOUT"
    REQ_OPERATION_INVALID = "REQ_OPERATION_INVALID"
    REQ_PAYLOAD_INVALID_JSON = "REQ_PAYLOAD_INVALID_JSON"
    REQ_PAYLOAD_UNSUPPORTED = "REQ_PAYLOAD_UNSUPPORTED"
    UNHANDLED_ERROR = "UNHANDLED_ERROR"
    UNKNOWN = "UNKNOWN"
    NO_ERROR = ""

    @classmethod
    def parse(cls, error: Optional[str] = None) -> AWSInfraServiceError:
        if not error:
            return cls.NO_ERROR

        try:
            code = error.split("::")[0]
            return cls(code)
        except ValueError:
            return cls.UNKNOWN


IGNORABLE_IP_TOKENS = [TokenTypes.AWS_INFRA, TokenTypes.WEB]
