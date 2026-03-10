# flake8: noqa: F405

from typing import Union

from pydantic import Field, BaseModel
from typing_extensions import Annotated

from .common import *  # noqa: F401,F403
from .adobe_pdf import *  # noqa: F401,F403
from .aws_infra import *  # noqa: F401,F403
from .aws_keys import *  # noqa: F401,F403
from .azure_id import *  # noqa: F401,F403
from .cc import *  # noqa: F401,F403
from .clonedsite import *  # noqa: F401,F403
from .cmd import *  # noqa: F401,F403
from .credit_card import *  # noqa: F401,F403
from .credit_card_v2 import *  # noqa: F401,F403
from .crowdstrike_cc import *  # noqa: F401,F403
from .cssclonedsite import *  # noqa: F401,F403
from .dns import *  # noqa: F401,F403
from .fast_redirect import *  # noqa: F401,F403
from .idp_app import *  # noqa: F401,F403
from .kubeconfig import *  # noqa: F401,F403
from .legacy import *  # noqa: F401,F403
from .log4shell import *  # noqa: F401,F403
from .ms_excel import *  # noqa: F401,F403
from .ms_word import *  # noqa: F401,F403
from .my_sql import *  # noqa: F401,F403
from .pwa import *  # noqa: F401,F403
from .qr_code import *  # noqa: F401,F403
from .signed_exe import *  # noqa: F401,F403
from .slack_api import *  # noqa: F401,F403
from .slow_redirect import *  # noqa: F401,F403
from .smtp import *  # noqa: F401,F403
from .sql_server import *  # noqa: F401,F403
from .svg import *  # noqa: F401,F403
from .svn import *  # noqa: F401,F403
from .web import *  # noqa: F401,F403
from .web_image import *  # noqa: F401,F403
from .webdav import *  # noqa: F401,F403
from .windows_dir import *  # noqa: F401,F403
from .windows_fake_fs import *  # noqa: F401,F403
from .wireguard import *  # noqa: F401,F403


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
        CrowdStrikeCCTokenRequest,
        SVGTokenRequest,
    ],
    Field(discriminator="token_type"),
]

AnyTokenEditRequest = Annotated[
    Union[AWSInfraTokenEditRequest,],
    Field(discriminator="token_type"),
]

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
        KubeconfigTokenResponse,
        CreditCardV2TokenResponse,
        IdPAppTokenResponse,
        AWSInfraTokenResponse,
        CrowdStrikeCCTokenResponse,
        SVGTokenResponse,
    ],
    Field(discriminator="token_type"),
]

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
        LegacyTokenHit,
        CreditCardV2TokenHit,
        IdPAppTokenHit,
        AWSInfraTokenHit,
        CrowdStrikeCCTokenHit,
        SVGTokenHit,
    ],
    Field(discriminator="token_type"),
]

AnyTokenExposedHit = AWSKeyTokenExposedHit

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
        LegacyTokenHistory,
        CreditCardV2TokenHistory,
        IdPAppTokenHistory,
        AWSInfraTokenHistory,
        CrowdStrikeCCTokenHistory,
        SVGTokenHistory,
    ],
    Field(discriminator="token_type"),
]


class HistoryResponse(BaseModel):
    canarydrop: Dict
    history: AnyTokenHistory
    google_api_key: Optional[str]


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
