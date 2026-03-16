# flake8: noqa: F401
# ruff: noqa: F401
from typing import Dict, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from .adobe_pdf import (
    DownloadPDFRequest,
    DownloadPDFResponse,
    PDFTokenHistory,
    PDFTokenHit,
    PDFTokenRequest,
    PDFTokenResponse,
)
from .aws_infra import (
    AWSInfraAssetField,
    AWSInfraAssetType,
    AWSInfraCheckRoleReceivedResponse,
    AWSInfraConfigStartRequest,
    AWSInfraConfigStartResponse,
    AWSInfraGenerateChildAssetsRequest,
    AWSInfraGenerateChildAssetsResponse,
    AWSInfraGenerateDataChoiceRequest,
    AWSInfraGenerateDataChoiceResponse,
    AWSInfraHandleRequest,
    AWSInfraHandleResponse,
    AWSInfraInventoryCustomerAccountReceivedResponse,
    AWSInfraManagementResponseRequest,
    AWSInfraOperationType,
    AWSInfraSavePlanRequest,
    AWSInfraServiceError,
    AWSInfraSetupIngestionReceivedResponse,
    AWSInfraState,
    AWSInfraTeardownReceivedResponse,
    AWSInfraTokenEditRequest,
    AWSInfraTokenHistory,
    AWSInfraTokenHit,
    AWSInfraTokenRequest,
    AWSInfraTokenResponse,
    AWSInfraTriggerOperationRequest,
    AwsInfraAdditionalInfo,
)
from .aws_keys import (
    AWSKey,
    AWSKeyAdditionalInfo,
    AWSKeyTokenExposedHit,
    AWSKeyTokenHistory,
    AWSKeyTokenHit,
    AWSKeyTokenRequest,
    AWSKeyTokenResponse,
    DownloadAWSKeysRequest,
    DownloadAWSKeysResponse,
)
from .azure_id import (
    AzureID,
    AzureIDAdditionalInfo,
    AzureIDTokenHistory,
    AzureIDTokenHit,
    AzureIDTokenRequest,
    AzureIDTokenResponse,
    DownloadAzureIDCertRequest,
    DownloadAzureIDCertResponse,
    DownloadAzureIDConfigRequest,
    DownloadAzureIDConfigResponse,
)
from .cc import (
    CCTokenHistory,
    CCTokenHit,
    CCTokenRequest,
    CCTokenResponse,
    CreditCard,
    DownloadCCRequest,
    DownloadCCResponse,
)
from .clonedsite import (
    ClonedWebTokenHistory,
    ClonedWebTokenHit,
    ClonedWebTokenRequest,
    ClonedWebTokenResponse,
)
from .cmd import (
    CMDTokenHistory,
    CMDTokenHit,
    CMDTokenRequest,
    CMDTokenResponse,
    DownloadCMDRequest,
    DownloadCMDResponse,
)
from .common import (
    CANARYTOKEN_RE,
    IGNORE_IP_UNSUPPORTED,
    READABLE_TOKEN_TYPE_NAMES,
    TOKEN_TYPES_WITH_ARTICLE_AN,
    AdditionalInfo,
    AlertStatus,
    Anonymous,
    AnySettingsRequest,
    BrowserScannerSettingsRequest,
    CanarydropSettingsTypes,
    Canarytoken,
    DefaultResponse,
    DeleteResponse,
    DownloadContentTypes,
    DownloadFmtTypes,
    DownloadGetRequestModel,
    DownloadIncidentListCSVRequest,
    DownloadIncidentListCSVResponse,
    DownloadIncidentListJsonRequest,
    DownloadIncidentListJsonResponse,
    DownloadZipRequest,
    DownloadZipResponse,
    EmailSettingsRequest,
    FetchLinksMessage,
    FetchLinksRequest,
    FetchLinksResponse,
    GeoIPBogonInfo,
    GeoIPInfo,
    HistoryPageRequest,
    Hostname,
    IPIgnoreListRequest,
    IPIgnoreSettingsRequest,
    ManagePageRequest,
    ManageResponse,
    Memo,
    PageRequest,
    Port,
    SettingsRequest,
    SettingsResponse,
    TokenAlertDetails,
    TokenExposedDetails,
    TokenExposedHit,
    TokenRequest,
    TokenTypes,
    User,
    WebImageSettingsRequest,
    WebhookSettingsRequest,
    response_error,
)
from .credit_card import ApiProvider
from .credit_card_v2 import (
    CreditCardV2AdditionalInfo,
    CreditCardV2TokenHistory,
    CreditCardV2TokenHit,
    CreditCardV2TokenRequest,
    CreditCardV2TokenResponse,
    DownloadCreditCardV2Request,
    DownloadCreditCardV2Response,
)
from .crowdstrike_cc import (
    CrowdStrikeCC,
    CrowdStrikeCCAdditionalInfo,
    CrowdStrikeCCTokenHistory,
    CrowdStrikeCCTokenHit,
    CrowdStrikeCCTokenRequest,
    CrowdStrikeCCTokenResponse,
)
from .cssclonedsite import (
    CSSClonedWebTokenHistory,
    CSSClonedWebTokenHit,
    CSSClonedWebTokenRequest,
    CSSClonedWebTokenResponse,
    DownloadCSSClonedWebRequest,
    DownloadCSSClonedWebResponse,
)
from .dns import (
    DNSTokenHistory,
    DNSTokenHit,
    DNSTokenRequest,
    DNSTokenResponse,
)
from .fast_redirect import (
    FastRedirectTokenHistory,
    FastRedirectTokenHit,
    FastRedirectTokenRequest,
    FastRedirectTokenResponse,
)
from .idp_app import (
    IdPAppTokenHistory,
    IdPAppTokenHit,
    IdPAppTokenRequest,
    IdPAppTokenResponse,
    IdPAppType,
)
from .kubeconfig import (
    DownloadKubeconfigRequest,
    DownloadKubeconfigResponse,
    KubeCerts,
    KubeconfigTokenHistory,
    KubeconfigTokenHit,
    KubeconfigTokenRequest,
    KubeconfigTokenResponse,
)
from .legacy import LegacyTokenHistory, LegacyTokenHit
from .log4shell import (
    Log4ShellTokenHistory,
    Log4ShellTokenHit,
    Log4ShellTokenRequest,
    Log4ShellTokenResponse,
)
from .ms_excel import (
    DownloadMSExcelRequest,
    DownloadMSExcelResponse,
    MsExcelDocumentTokenHistory,
    MsExcelDocumentTokenHit,
    MsExcelDocumentTokenRequest,
    MsExcelDocumentTokenResponse,
)
from .ms_word import (
    DownloadMSWordRequest,
    DownloadMSWordResponse,
    MsWordDocumentTokenHistory,
    MsWordDocumentTokenHit,
    MsWordDocumentTokenRequest,
    MsWordDocumentTokenResponse,
)
from .my_sql import (
    DownloadMySQLRequest,
    DownloadMySQLResponse,
    MySQLTokenHistory,
    MySQLTokenHit,
    MySQLTokenRequest,
    MySQLTokenResponse,
)
from .pwa import (
    PWA_APP_TITLES,
    PWATokenHistory,
    PWATokenHit,
    PWATokenRequest,
    PWATokenResponse,
    PWAType,
)
from .qr_code import (
    DownloadQRCodeRequest,
    DownloadQRCodeResponse,
    QRCodeTokenHistory,
    QRCodeTokenHit,
    QRCodeTokenRequest,
    QRCodeTokenResponse,
)
from .signed_exe import (
    CustomBinaryTokenHistory,
    CustomBinaryTokenHit,
    CustomBinaryTokenRequest,
    CustomBinaryTokenResponse,
    UploadedExe,
)
from .slack_api import (
    DownloadSlackAPIRequest,
    DownloadSlackAPIResponse,
    SlackAPITokenHistory,
    SlackAPITokenHit,
)
from .slow_redirect import (
    SlowRedirectTokenHistory,
    SlowRedirectTokenHit,
    SlowRedirectTokenRequest,
    SlowRedirectTokenResponse,
)
from .smtp import (
    SMTPHeloField,
    SMTPMailField,
    SMTPTokenHistory,
    SMTPTokenHit,
    SMTPTokenRequest,
    SMTPTokenResponse,
)
from .sql_server import (
    SQLServerTokenHistory,
    SQLServerTokenHit,
    SQLServerTokenRequest,
    SQLServerTokenResponse,
)
from .svg import (
    DownloadSVGRequest,
    DownloadSVGResponse,
    SVGTokenHistory,
    SVGTokenHit,
    SVGTokenRequest,
    SVGTokenResponse,
)
from .svn import (
    SvnTokenHistory,
    SvnTokenHit,
    SvnTokenRequest,
    SvnTokenResponse,
)
from .web import (
    WebBugTokenHistory,
    WebBugTokenHit,
    WebBugTokenRequest,
    WebBugTokenResponse,
)
from .web_image import (
    CustomImageTokenHistory,
    CustomImageTokenHit,
    CustomImageTokenRequest,
    CustomImageTokenResponse,
    UploadedImage,
)
from .webdav import (
    WebDavAdditionalInfo,
    WebDavTokenHistory,
    WebDavTokenHit,
    WebDavTokenRequest,
    WebDavTokenResponse,
)
from .windows_dir import (
    WindowsDirectoryTokenHistory,
    WindowsDirectoryTokenHit,
    WindowsDirectoryTokenRequest,
    WindowsDirectoryTokenResponse,
)
from .windows_fake_fs import (
    DownloadWindowsFakeFSRequest,
    DownloadWindowsFakeFSResponse,
    WindowsFakeFSTokenHistory,
    WindowsFakeFSTokenHit,
    WindowsFakeFSTokenRequest,
    WindowsFakeFSTokenResponse,
)
from .wireguard import (
    WireguardTokenHistory,
    WireguardTokenHit,
    WireguardTokenRequest,
    WireguardTokenResponse,
)


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
