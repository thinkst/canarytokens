import os
from typing import Any, Literal, Optional

from canarytokens.utils import strtobool
from pydantic import EmailStr, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from canarytokens.models import Port


class SwitchboardSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../switchboard/switchboard.env",
        env_file_encoding="utf-8",
        env_prefix="CANARY_",
        frozen=True,
    )

    PUBLIC_DOMAIN: str
    CHANNEL_DNS_IP: str = ""
    CHANNEL_DNS_PORT: Port = Port(5354)
    CHANNEL_HTTP_PORT: Port = Port(8083)
    CHANNEL_SMTP_PORT: Port = Port(2500)
    CHANNEL_MYSQL_PORT: Port = Port(3306)
    CHANNEL_MTLS_KUBECONFIG_PORT: Port = Port(6443)
    CHANNEL_WIREGUARD_PORT: Port = Port(51820)
    SWITCHBOARD_SCHEME: str = "https"
    FORCE_HTTPS: bool = False
    # TODO: Remove this default here and added it where it's used. This is too opinionated.
    REDIS_HOST: str = "localhost" if strtobool(os.getenv("CI", "False")) else "redis"
    REDIS_PORT: Port = Port(6379)
    REDIS_DB: str = "0"

    REAL_IP_HEADER: str = "x-real-ip"

    WG_PRIVATE_KEY_SEED: str
    WG_PRIVATE_KEY_N: str = "1000"

    FRONTEND_SETTINGS_PATH: str = "../frontend/frontend.env"
    USING_NGINX: bool = True
    TEMPLATES_PATH: str = "../templates"

    ALERT_EMAIL_FROM_ADDRESS: EmailStr = "your-email@example.com"
    ALERT_EMAIL_FROM_DISPLAY: str = "Canarytokens-Test"
    ALERT_EMAIL_SUBJECT: str = "Canarytokens Alert"
    MAX_HISTORY: int = 50
    MAX_ALERTS_PER_MINUTE: int = 1
    # Maximum number of alert failures before a mechanism is disabled
    MAX_ALERT_FAILURES: int = 5

    IPINFO_API_KEY: Optional[SecretStr] = None
    # Mailgun Required Settings
    MAILGUN_API_KEY: Optional[SecretStr] = None
    MAILGUN_BASE_URL: Optional[HttpUrl] = HttpUrl("https://api.mailgun.net")
    MAILGUN_DOMAIN_NAME: Optional[str] = None
    # Sendgrid Required Settings
    SENDGRID_API_KEY: Optional[SecretStr] = None
    SENDGRID_SANDBOX_MODE: bool = True
    # SMTP Required Settings
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[Port] = Port(587)

    SENTRY_DSN: Optional[HttpUrl] = None
    SENTRY_ENVIRONMENT: Literal["prod", "staging", "dev", "ci", "local"] = "local"
    SENTRY_ENABLE: bool = True

    SWITCHBOARD_LOG_SIZE: Optional[int] = 500000000
    SWITCHBOARD_LOG_COUNT: Optional[int] = 20

    TOKEN_RETURN: Literal["gif", "fortune"] = "gif"
    LAMBDA_AWS_CRED_REPORT_AUTH: Optional[str] = None


class FrontendSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../frontend/frontend.env",
        env_file_encoding="utf-8",
        env_prefix="CANARY_",
        enable_decoding=False,
        frozen=True,
    )

    API_APP_TITLE: str = "Canarytokens"
    API_VERSION_STR: str = "v1"
    PUBLIC_IP: str
    DOMAINS: list[str]
    NXDOMAINS: list[str]
    SWITCHBOARD_SETTINGS_PATH: str = "../switchboard/switchboard.env"

    SENTRY_DSN: Optional[HttpUrl] = None
    SENTRY_ENVIRONMENT: Literal["prod", "staging", "dev", "ci", "local"] = "local"
    SENTRY_ENABLE: bool = True

    TEMPLATES_PATH: str = "../templates"
    STATIC_FILES_PATH: str = "../templates/static"
    STATIC_FILES_APPLICATION_SUB_PATH: str = "/resources"
    STATIC_FILES_APPLICATION_INTERNAL_NAME: str = "resources"
    TOKENS_FETCH_LIMIT: int = 1000

    # if None the API docs won't load. Loads at /API_HASH/{your_url}. Must start with a /
    API_REDOC_URL: Optional[str] = None

    # upload settings
    MAX_UPLOAD_SIZE: int = 1024 * 1024 * 1
    WEB_IMAGE_UPLOAD_PATH: str = "/uploads"

    # ! UNUSED ! TODO: figure out why
    # log settings

    FRONTEND_LOG_SIZE: Optional[int] = 500000000
    FRONTEND_LOG_COUNT: Optional[int] = 20

    DEV_BUILD_ID: Optional[str] = None

    # 3rd party settings
    AWSID_URL: Optional[HttpUrl] = None
    AWSID_AUTH: Optional[str] = None
    AWSID_GUID: Optional[str] = None
    AWSID_CONTROL_ACCOUNT_ID: Optional[str] = None
    TESTING_AWS_ACCESS_KEY_ID: Optional[str] = ""
    TESTING_AWS_SECRET_ACCESS_KEY: Optional[str] = ""
    TESTING_AWS_REGION: Optional[str] = "us-east-2"
    TESTING_AWSID_AUTH: Optional[str] = "test_auth_value"
    TESTING_AWS_OUTPUT: Optional[str] = "json"
    AZURE_ID_TOKEN_URL: Optional[HttpUrl] = None
    AZURE_ID_TOKEN_AUTH: Optional[str] = None
    CROWDSTRIKE_CC_CREATE_URL: Optional[HttpUrl] = None
    CROWDSTRIKE_CC_DELETE_URL: Optional[HttpUrl] = None
    GOOGLE_API_KEY: Optional[str] = None
    EXTEND_EMAIL: Optional[str] = None
    EXTEND_PASSWORD: Optional[SecretStr] = SecretStr("NoExtendPasswordFound")
    EXTEND_CARD_NAME: Optional[str] = None
    CLOUDFRONT_URL: HttpUrl = "https://SET-CLOUDFRONT-URL-IN-FRONTEND-DOT-ENV.invalid"
    CLOUDFLARE_ACCOUNT_ID: Optional[str] = ""
    CLOUDFLARE_NAMESPACE: Optional[str] = ""
    CLOUDFLARE_API_TOKEN: Optional[str] = ""
    WEBDAV_SERVER: Optional[str] = ""
    AZUREAPP_ID: Optional[str] = None
    AZUREAPP_SECRET: Optional[str] = (
        None  # TODO: Figure out SecretStr with Azure secrets
    )
    CREDIT_CARD_TOKEN_ENABLED: bool = False
    CREDIT_CARD_INFRA_CUSTOMER_GUID: Optional[str] = None
    CREDIT_CARD_INFRA_CUSTOMER_SECRET: Optional[str] = None
    CREDIT_CARD_INFRA_LAMBDA: Optional[str] = None
    CREDIT_CARD_INFRA_ACCOUNT_ID: Optional[str] = None
    CREDIT_CARD_INFRA_REGION: Optional[str] = None
    CREDIT_CARD_INFRA_ACCESS_ROLE: Optional[str] = None
    CLOUDFLARE_TURNSTILE_SECRET: Optional[str] = None
    MCP_SERVER_URLS: Optional[list[str]] = [""]
    MCP_SERVER_SECRET: Optional[str] = "abcD0123defG4567"

    AWS_INFRA_AWS_ACCOUNT: Optional[str] = None
    AWS_INFRA_AWS_REGION: Optional[str] = None
    AWS_INFRA_SHARED_SECRET: Optional[str] = None
    AWS_INFRA_MANAGEMENT_REQUEST_SQS_URL: Optional[str] = None
    AWS_INFRA_CALLBACK_DOMAIN: Optional[str] = "callback domain goes here"
    AWS_INFRA_INGESTION_BUS: Optional[str] = None
    AWS_INFRA_TF_MODULE_BUCKET: Optional[str] = None
    AWS_INFRA_NAME_GENERATION_LIMIT: Optional[int] = 50
    AWS_INFRA_CLEANUP_INTERVAL_SECONDS: int = 6 * 60 * 60
    AWS_INFRA_CLEANUP_MAX_AGE: int = 7 * 24 * 60 * 60
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: Optional[str] = "gemini-2.5-flash"
    GEMINI_PROMPT_TEMPLATE: Optional[str] = None
    GEMINI_SYSTEM_PROMPT: Optional[str] = None
    GEMINI_TEMPERATURE: Optional[str] = "1.8"
    DEFAULT_GUARDRAIL_TRIGGERS: list[str] = []

    # for local aws infra testing
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None

    @field_validator("DOMAINS", "NXDOMAINS", "MCP_SERVER_URLS", mode="before")
    @classmethod
    def parse_csv_list(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [item for item in value.split(",")]
        return value

    @field_validator("DEFAULT_GUARDRAIL_TRIGGERS", mode="before")
    @classmethod
    def parse_guardrail_triggers(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value
