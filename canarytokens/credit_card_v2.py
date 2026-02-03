import boto3
import botocore
import socket
import json

from canarytokens.settings import FrontendSettings
from canarytokens.models import Canarytoken
from dataclasses import dataclass
from typing import Optional, Tuple, Literal, Union
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum  # Python 3.11+
else:
    from backports.strenum import StrEnum  # Python < 3.11
from pydantic import BaseModel


frontend_settings = FrontendSettings()


_CACHED_LAMBDA_CLIENT = None
_RETRY_COUNT = 2


class Lambda(StrEnum):
    PAYMENTS_DEMO = "CreditCardPaymentsDemoBackend"


class _Api(StrEnum):
    CARD_CREATE = "/card/create"
    CUSTOMER_DETAILS = "/customer/details"


class Status(StrEnum):
    SUCCESS = "success"
    CUSTOMER_NOT_FOUND = "customer_not_found"
    NO_AVAILABLE_CARDS = "no_cards"
    NO_MORE_CREDITS = "no_more_credits"
    ERROR = "error"
    FORBIDDEN = "forbidden"


class TriggerWebhookEvent(StrEnum):
    TransactionFailed = "issuing.transaction.failed"
    ThreeDSecureNotification = "issuing.3ds_notification.stepup_otp"


@dataclass(frozen=True)
class CreditCard:
    card_id: str
    card_number: str
    cvv: str
    expiry_month: int
    expiry_year: int
    name_on_card: str


@dataclass(frozen=True)
class Customer:
    guid: str
    created: str
    canarytoken_domain: str
    cards_quota: int
    cards_assigned: int


class CreditCardTrigger3DSNotification(BaseModel):
    trigger_type: Literal[TriggerWebhookEvent.ThreeDSecureNotification] = (
        TriggerWebhookEvent.ThreeDSecureNotification
    )
    canarytoken: Optional[str]
    masked_card_number: Optional[str]
    transaction_amount: Optional[str]
    transaction_currency: Optional[str]


class CreditCardTriggerTransaction(BaseModel):
    trigger_type: Literal[TriggerWebhookEvent.TransactionFailed] = (
        TriggerWebhookEvent.TransactionFailed
    )
    canarytoken: Canarytoken
    masked_card_number: Optional[str]
    merchant: Optional[str]
    transaction_amount: Optional[str]
    transaction_currency: Optional[str]
    transaction_date: Optional[str]
    transaction_type: Optional[str]
    status: Optional[str]


AnyCreditCardTrigger = Union[
    CreditCardTrigger3DSNotification,
    CreditCardTriggerTransaction,
]


def _get_lambda_client(refresh_client: bool = False):
    """Creates a botocore session and grabs sts client.
    This allows for getting assumed role creds without polluting
    or misusing the default boto3 session.

    Using these sts creds a client is returned for a `service_name` service.

    Returns:
        boto3.Client: boto3 client of the Lambda service.
    """
    global _CACHED_LAMBDA_CLIENT

    if _CACHED_LAMBDA_CLIENT is not None and not refresh_client:
        return _CACHED_LAMBDA_CLIENT

    botocore_session = botocore.session.get_session()
    botocore_session.set_config_variable("CREDENTIALS_FILE".lower(), "")
    botocore_session.set_config_variable("SHARED_CREDENTIALS_FILE".lower(), "")
    botocore_session.set_config_variable("CONFIG_FILE".lower(), "")
    session = boto3.Session(botocore_session=botocore_session)
    client = session.client("sts").assume_role(
        RoleArn=f"arn:aws:iam::{frontend_settings.CREDIT_CARD_INFRA_ACCOUNT_ID}:role/{frontend_settings.CREDIT_CARD_INFRA_ACCESS_ROLE}",
        RoleSessionName=socket.gethostname(),
    )
    client_session = boto3.session.Session()
    _CACHED_LAMBDA_CLIENT = client_session.client(
        "lambda",
        region_name=frontend_settings.CREDIT_CARD_INFRA_REGION,
        aws_access_key_id=client["Credentials"]["AccessKeyId"],
        aws_secret_access_key=client["Credentials"]["SecretAccessKey"],
        aws_session_token=client["Credentials"]["SessionToken"],
    )

    return _CACHED_LAMBDA_CLIENT


def _invoke_lambda(lambda_name: str, payload: dict) -> dict:
    client = _get_lambda_client()

    for attempt in range(_RETRY_COUNT):
        try:
            return client.invoke(
                FunctionName=lambda_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )
        except botocore.exceptions.ClientError as err:
            if (
                err.response["Error"]["Code"] == "ExpiredTokenException"
                and attempt < _RETRY_COUNT - 1
            ):
                client = _get_lambda_client(refresh_client=True)
                continue
            raise err


def create_card(canarytoken: str) -> Tuple[Status, Optional[CreditCard]]:
    if not frontend_settings.CREDIT_CARD_TOKEN_ENABLED:
        return (Status.ERROR, None)

    payload = {
        "api": _Api.CARD_CREATE.value,
        "guid": frontend_settings.CREDIT_CARD_INFRA_CUSTOMER_GUID,
        "secret": frontend_settings.CREDIT_CARD_INFRA_CUSTOMER_SECRET,
        "canarytoken": canarytoken,
    }

    response = _invoke_lambda(frontend_settings.CREDIT_CARD_INFRA_LAMBDA, payload)
    response_payload = json.loads(response["Payload"].read())

    status = Status(response_payload.get("status"))

    if status == Status.SUCCESS:
        return (Status.SUCCESS, CreditCard(**response_payload["body"]["card"]))

    return (status, None)


def get_customer_details() -> Tuple[Status, Optional[Customer]]:
    if not frontend_settings.CREDIT_CARD_TOKEN_ENABLED:
        return (Status.ERROR, None)

    payload = {
        "api": _Api.CUSTOMER_DETAILS.value,
        "guid": frontend_settings.CREDIT_CARD_INFRA_CUSTOMER_GUID,
        "secret": frontend_settings.CREDIT_CARD_INFRA_CUSTOMER_SECRET,
    }

    response = _invoke_lambda(frontend_settings.CREDIT_CARD_INFRA_LAMBDA, payload)
    response_payload = json.loads(response["Payload"].read())

    status = Status(response_payload.get("status"))

    if status == Status.SUCCESS:
        return (Status.SUCCESS, Customer(**response_payload["body"]["customer"]))

    return (status, None)


def trigger_demo_alert(card_id: str, card_number: str) -> Status:
    if not frontend_settings.CREDIT_CARD_TOKEN_ENABLED:
        return Status.ERROR

    if card_id is None or card_number is None:
        return Status.ERROR

    payload = {
        "card_id": card_id,
        "card_number": card_number,
    }

    response = _invoke_lambda(Lambda.PAYMENTS_DEMO.value, payload)
    response_payload = json.loads(response["Payload"].read())

    return Status(response_payload.get("status"))
