from typing import List, Literal, Optional
from .common import (
    AdditionalInfo,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
    enum,
)


class IdPAppType(enum.StrEnum):
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


class IdPAppTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.IDP_APP] = TokenTypes.IDP_APP
    entity_id: str
    app_type: IdPAppType


class IdPAppTokenHit(TokenHit):
    token_type: Literal[TokenTypes.IDP_APP] = TokenTypes.IDP_APP
    additional_info: AdditionalInfo = AdditionalInfo()


class IdPAppTokenHistory(TokenHistory[IdPAppTokenHit]):
    token_type: Literal[TokenTypes.IDP_APP] = TokenTypes.IDP_APP
    hits: List[IdPAppTokenHit] = []
