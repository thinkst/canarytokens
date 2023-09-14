import os
from distutils.util import strtobool
from typing import Any, Literal, Optional

from pydantic import BaseSettings, EmailStr, HttpUrl, SecretStr

from canarytokens.models import Port


class SwitchboardSettings(BaseSettings):
    PUBLIC_DOMAIN: str
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

    WG_PRIVATE_KEY_SEED: str
    WG_PRIVATE_KEY_N: str = "1000"

    FRONTEND_SETTINGS_PATH: str = "../frontend/frontend.env"
    USING_NGINX: bool = True
    TEMPLATES_PATH: str = "../templates"

    ALERT_EMAIL_FROM_ADDRESS: EmailStr = EmailStr("illegal@email.com")
    ALERT_EMAIL_FROM_DISPLAY: str = "Canarytokens-Test"
    ALERT_EMAIL_SUBJECT: str = "Canarytokens Alert"
    MAX_ALERTS_PER_MINUTE: int = 1
    # Maximum number of alert failures before a mechanism is disabled
    MAX_ALERT_FAILURES: int = 5

    IPINFO_API_KEY: Optional[SecretStr] = None

    MAILGUN_API_KEY: Optional[SecretStr] = SecretStr("NoSendgridAPIKeyFound")
    MAILGUN_BASE_URL: Optional[HttpUrl] = HttpUrl(
        "https://api.mailgun.net", scheme="https"
    )
    MAILGUN_DOMAIN_NAME: Optional[str]
    SENDGRID_API_KEY: Optional[SecretStr] = SecretStr("NoSendgridAPIKeyFound")
    SENDGRID_SANDBOX_MODE: bool = True

    SENTRY_DSN: Optional[HttpUrl] = None
    SENTRY_ENVIRONMENT: Literal["prod", "staging", "dev", "ci", "local"] = "local"
    SENTRY_ENABLE: bool = True

    SWITCHBOARD_LOG_SIZE: Optional[int] = 500000000
    SWITCHBOARD_LOG_COUNT: Optional[int] = 20

    TOKEN_RETURN: Literal["gif", "fortune"] = "gif"

    class Config:
        allow_mutation = False
        env_file = "../switchboard/switchboard.env"
        env_file_encoding = "utf-8"
        env_prefix = "CANARY_"


class FrontendSettings(BaseSettings):
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

    # upload settings
    MAX_UPLOAD_SIZE: int = 1024 * 1024 * 1
    WEB_IMAGE_UPLOAD_PATH: str = "/uploads"

    # ! UNUSED ! TODO: figure out why
    # log settings

    FRONTEND_LOG_SIZE: Optional[int] = 500000000
    FRONTEND_LOG_COUNT: Optional[int] = 20

    DEV_BUILD_ID: Optional[str]

    # 3rd party settings
    AWSID_URL: Optional[HttpUrl]
    TESTING_AWS_ACCESS_KEY_ID: Optional[str] = ""
    TESTING_AWS_SECRET_ACCESS_KEY: Optional[str] = ""
    TESTING_AWS_REGION: Optional[str] = "us-east-2"
    TESTING_AWS_OUTPUT: Optional[str] = "json"
    AZURE_ID_TOKEN_URL: Optional[HttpUrl]
    AZURE_ID_TOKEN_AUTH: Optional[str]
    GOOGLE_API_KEY: Optional[str]
    EXTEND_EMAIL: Optional[str]
    EXTEND_PASSWORD: Optional[SecretStr] = SecretStr("NoExtendPasswordFound")
    EXTEND_CARD_NAME: Optional[str]
    GLPAT_URL: Optional[HttpUrl]
    GLPAT_API_KEY: Optional[SecretStr] = SecretStr("NoGitLabAPIKeyFound")
    TESTING_GLPAT_TOKEN: Optional[str]
    TESTING_GLPAT_EXPIRY: Optional[str]

    class Config:
        allow_mutation = False
        env_file = "../frontend/frontend.env"
        env_file_encoding = "utf-8"
        env_prefix = "CANARY_"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name in ["DOMAINS", "NXDOMAINS"]:
                return [x for x in raw_val.split(",")]
            return cls.json_loads(raw_val)
