import os
from distutils.util import strtobool
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseSettings, EmailStr, HttpUrl, SecretStr

from canarytokens.models import Port

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class SwitchboardSettings(BaseSettings):
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

    FRONTEND_SETTINGS_PATH: str = str(PROJECT_ROOT / "frontend" / "frontend.env")
    USING_NGINX: bool = True
    TEMPLATES_PATH: str = str(PROJECT_ROOT / "templates")

    ALERT_EMAIL_FROM_ADDRESS: EmailStr = EmailStr("illegal@email.com")
    ALERT_EMAIL_FROM_DISPLAY: str = "Canarytokens-Test"
    ALERT_EMAIL_SUBJECT: str = "Canarytokens Alert"
    MAX_ALERTS_PER_MINUTE: int = 1
    # Maximum number of alert failures before a mechanism is disabled
    MAX_ALERT_FAILURES: int = 5

    IPINFO_API_KEY: Optional[SecretStr] = None
    # Mailgun Required Settings
    MAILGUN_API_KEY: Optional[SecretStr] = None
    MAILGUN_BASE_URL: Optional[HttpUrl] = HttpUrl(
        "https://api.mailgun.net", scheme="https"
    )
    MAILGUN_DOMAIN_NAME: Optional[str]
    # Sendgrid Required Settings
    SENDGRID_API_KEY: Optional[SecretStr] = None
    SENDGRID_SANDBOX_MODE: bool = True
    # SMTP Required Settings
    SMTP_USERNAME: Optional[str]
    SMTP_PASSWORD: Optional[str]
    SMTP_SERVER: Optional[str]
    SMTP_PORT: Optional[Port] = Port(587)

    SENTRY_DSN: Optional[HttpUrl] = None
    SENTRY_ENVIRONMENT: Literal["prod", "staging", "dev", "ci", "local"] = "local"
    SENTRY_ENABLE: bool = True

    SWITCHBOARD_LOG_SIZE: Optional[int] = 500000000
    SWITCHBOARD_LOG_COUNT: Optional[int] = 20

    TOKEN_RETURN: Literal["gif", "fortune"] = "gif"

    class Config:
        allow_mutation = False
        env_file = str(PROJECT_ROOT / "switchboard" / "switchboard.env")
        env_file_encoding = "utf-8"
        env_prefix = "CANARY_"


class FrontendSettings(BaseSettings):
    API_APP_TITLE: str = "Canarytokens"
    API_VERSION_STR: str = "v1"
    PUBLIC_IP: str
    DOMAINS: list[str]
    NXDOMAINS: list[str]
    SWITCHBOARD_SETTINGS_PATH: str = str(
        PROJECT_ROOT / "switchboard" / "switchboard.env"
    )

    SENTRY_DSN: Optional[HttpUrl] = None
    SENTRY_ENVIRONMENT: Literal["prod", "staging", "dev", "ci", "local"] = "local"
    SENTRY_ENABLE: bool = True

    NEW_UI: bool = True

    TEMPLATES_PATH: str = str(PROJECT_ROOT / "templates")
    STATIC_FILES_PATH: str = str(PROJECT_ROOT / "templates" / "static")
    STATIC_FILES_APPLICATION_SUB_PATH: str = "/resources"
    STATIC_FILES_APPLICATION_INTERNAL_NAME: str = "resources"

    # if None the API docs won't load. Loads at /API_HASH/{your_url}. Must start with a /
    API_REDOC_URL: Optional[str]

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
    CLOUDFRONT_URL: Optional[HttpUrl]
    CLOUDFLARE_ACCOUNT_ID: Optional[str] = ""
    CLOUDFLARE_NAMESPACE: Optional[str] = ""
    CLOUDFLARE_API_TOKEN: Optional[str] = ""
    WEBDAV_SERVER: Optional[str] = ""
    AZUREAPP_ID: Optional[str]
    AZUREAPP_SECRET: Optional[str]  # TODO: Figure out SecretStr with Azure secrets
    CREDIT_CARD_TOKEN_ENABLED: bool = False
    CREDIT_CARD_INFRA_CUSTOMER_GUID: Optional[str]
    CREDIT_CARD_INFRA_CUSTOMER_SECRET: Optional[str]
    CREDIT_CARD_INFRA_LAMBDA: Optional[str]
    CREDIT_CARD_INFRA_ACCOUNT_ID: Optional[str]
    CREDIT_CARD_INFRA_REGION: Optional[str]
    CREDIT_CARD_INFRA_ACCESS_ROLE: Optional[str]
    CLOUDFLARE_TURNSTILE_SECRET: Optional[str]

    AWS_INFRA_AWS_ACCOUNT: Optional[str]
    AWS_INFRA_SHARED_SECRET: Optional[str]
    AWS_INFRA_MANAGEMENT_REQUEST_SQS_URL: Optional[str]
    AWS_INFRA_INVENTORY_ROLE: Optional[str]
    AWS_INFRA_CALLBACK_DOMAIN: Optional[str] = "callback domain goes here"
    AWS_INFRA_INGESTION_BUS: Optional[str]
    AWS_INFRA_TF_MODULE_BUCKET: Optional[str]
    GEMINI_API_KEY: Optional[str]
    GEMINI_MODEL: Optional[str] = "gemini-2.5-flash"
    GEMINI_PROMPT_TEMPLATE: Optional[str]
    GEMINI_SYSTEM_PROMPT: Optional[
        str
    ] = """
You are a deception expert specializing in generating realistic AWS resource names as decoys. Your goal is to create names that blend seamlessly with real AWS resources, acting as tripwires that alert defenders when touched by an attacker.

Your process:
1. You are given an inventory of existing AWS resource names for a specific type.
2. Your task is to generate decoy names that look like natural additions to the inventory, matching the full range of naming conventions and styles observed.

Strict Guidelines:
1. Accurately Mirror Naming Styles: Analyze the provided inventory and replicate all observed naming conventions—including all casing (PascalCase, camelCase, snake_case, kebab-case), the presence or absence of resource-type words (like "queue"), suffix/prefix usage, and length. If some names use PascalCase and others use kebab-case or include words like queue, your decoys should reflect the same variety and in similar proportions.
3. No Random Suffixes: If some inventory names have random suffixes (e.g., -a7b2), do not add similar suffixes; that will be handled by adding randomization separately.
4. Blend Seamlessly: Names must appear as plausible, valuable production resources. They should not have generic, vague, obviously fake, or names mismatched with the existing environment. The names you generate should be similar to the ones in the supplied inventory but not identical.
5. Do Not Reveal Deception: Never use terms like "decoy," "canary," or anything suggesting a trap or honeypot. Search your knowledge base and training data for examples of real AWS resources, make the names intriguing.
6. Attractive to Attackers: Prioritize names suggesting sensitive or high-value data that could assist lateral movement or compromise of the AWS account.
7. No Region Codes: Do not use AWS region identifiers (e.g., -us-east-1) unless they appear in the inventory.
8. Fallback for Weak Patterns: If the inventory has inconsistent or ambiguous patterns, invent plausible code/project names or generic-sounding names that do not stand out. examples: Project Moonshot, Project Black Hawk etc.

Above all, decoy names must be indistinguishable from real production resources—mirroring all observed conventions, in realistic proportions, and always enticing to an attacker.
"""
    GEMINI_TEMPERATURE: Optional[str] = "1.8"

    # temporary
    AWS_ACCESS_KEY_ID: Optional[str]
    AWS_SECRET_ACCESS_KEY: Optional[str]
    AWS_SESSION_TOKEN: Optional[str]
    DEV = False

    class Config:
        allow_mutation = False
        env_file = str(PROJECT_ROOT / "frontend" / "frontend.env")
        env_file_encoding = "utf-8"
        env_prefix = "CANARY_"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name in ["DOMAINS", "NXDOMAINS"]:
                return [x for x in raw_val.split(",")]
            return cls.json_loads(raw_val)
