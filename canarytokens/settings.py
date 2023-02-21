import os
from distutils.util import strtobool
from typing import List, Literal, Optional

from pydantic import BaseSettings, EmailStr, HttpUrl, SecretStr

from canarytokens.models import Port


class Settings(BaseSettings):

    CHANNEL_DNS_PORT: Port = Port(5354)
    CHANNEL_HTTP_PORT: Port = Port(8083)
    CHANNEL_SMTP_PORT: Port = Port(2500)
    CHANNEL_MYSQL_PORT: Port = Port(3306)
    CHANNEL_MTLS_KUBECONFIG_PORT: Port = Port(6443)
    CHANNEL_WIREGUARD_PORT: Port = Port(51820)
    # TODO: Remove this default here and added it where it's used. This is too opinionated.
    REDIS_HOST: str = "localhost" if strtobool(os.getenv("CI", "False")) else "redis"
    REDIS_PORT: Port = Port(6379)
    REDIS_DB: str = "0"

    AWSID_URL: HttpUrl
    TESTING_AWS_ACCESS_KEY_ID: Optional[str]
    TESTING_AWS_SECRET_ACCESS_KEY: Optional[str]
    TESTING_AWS_REGION: Optional[str] = "us-east-2"
    TESTING_AWS_OUTPUT: Optional[str] = "json"

    WG_PRIVATE_KEY_SEED: str
    WG_PRIVATE_KEY_N: str = "1000"

    LISTEN_DOMAIN: str
    PUBLIC_IP: str
    NXDOMAINS: List[str]
    DOMAINS: List[str]
    FRONTEND_SETTINGS_PATH: str
    USING_NGINX: bool = False
    TEMPLATES_PATH: str = "../templates"

    ALERT_EMAIL_FROM_ADDRESS: EmailStr = EmailStr("illegal@email.com")
    ALERT_EMAIL_FROM_DISPLAY: str = "Canarytokens-Test"
    ALERT_EMAIL_SUBJECT: str = "Canarytokens Alert"
    SENDGRID_API_KEY: SecretStr = SecretStr("NoSendgridAPIKeyFound")
    SENDGRID_SANDBOX_MODE: bool = True

    SENTRY_DSN: HttpUrl
    SENTRY_ENVIRONMENT: Literal["prod", "staging", "dev", "ci", "local"] = "local"

    TOKEN_RETURN: Literal["gif", "fortune"] = "gif"

    class Config:
        allow_mutation = False
        env_file = "switchboard.env"
        env_file_encoding = "utf-8"
        env_prefix = "CANARY_"


class FrontendSettings(BaseSettings):

    API_APP_TITLE: str = "Canarytokens"
    API_VERSION_STR: str = "v1"
    FRONTEND_HOSTNAME: str
    FRONTEND_SCHEME: str
    SWITCHBOARD_SETTINGS_PATH: str

    SENTRY_DSN: HttpUrl
    SENTRY_ENVIRONMENT: Literal["prod", "staging", "dev", "ci", "local"] = "local"

    TEMPLATES_PATH: str = "../templates"
    STATIC_FILES_PATH: str
    STATIC_FILES_APPLICATION_SUB_PATH: str
    STATIC_FILES_APPLICATION_INTERNAL_NAME: str

    TOKEN_RETURN: Literal["gif", "fortune"] = "gif"

    # upload settings
    MAX_WEB_IMAGE_UPLOAD_SIZE: int = 1024 * 1024 * 1
    WEB_IMAGE_UPLOAD_PATH: str = "/root/uploads"

    # exe/ddl upload settings
    MAX_EXE_UPLOAD_SIZE: int = 1024 * 1024 * 1

    # 3rd party settings
    GOOGLE_API_KEY: str

    class Config:
        allow_mutation = False
        env_file = "frontend.env"
        env_file_encoding = "utf-8"
        env_prefix = "CANARY_"
