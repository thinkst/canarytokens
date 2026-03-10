from typing import List, Literal, Optional

from pydantic import BaseModel

from canarytokens.utils import json_safe_dict
from .common import (
    DownloadContentTypes,
    DownloadFmtTypes,
    TokenDownloadRequest,
    TokenDownloadResponse,
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class CreditCardV2AdditionalInfo(BaseModel):
    merchant: Optional[str]
    merchant_identifier: Optional[str]
    transaction_amount: Optional[str]
    transaction_currency: Optional[str]
    masked_card_number: Optional[str]
    transaction_date: Optional[str]
    transaction_type: Optional[str]
    status: Optional[str]


class CreditCardV2TokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.CREDIT_CARD_V2] = TokenTypes.CREDIT_CARD_V2
    cf_turnstile_response: Optional[str]


class CreditCardV2TokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.CREDIT_CARD_V2] = TokenTypes.CREDIT_CARD_V2
    card_id: str
    name_on_card: str
    card_number: str
    cvv: str
    expiry_month: int
    expiry_year: int


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


class CreditCardV2TokenHistory(TokenHistory[CreditCardV2TokenHit]):
    token_type: Literal[TokenTypes.CREDIT_CARD_V2] = TokenTypes.CREDIT_CARD_V2
    hits: List[CreditCardV2TokenHit] = []


class DownloadCreditCardV2Request(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.CREDIT_CARD_V2] = DownloadFmtTypes.CREDIT_CARD_V2


class DownloadCreditCardV2Response(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.TEXTPLAIN] = (
        DownloadContentTypes.TEXTPLAIN
    )
    filename: str = "credit_card"
    token: str
    auth: str
