from typing import List, Literal, Optional, Union

from canarytokens.models.smtp import SMTPMailField
from .common import AdditionalInfo, TokenHistory, TokenHit, TokenTypes


class LegacyTokenHit(TokenHit):
    token_type: Literal[TokenTypes.LEGACY] = TokenTypes.LEGACY
    src_data: Optional[dict]
    request_headers: Optional[dict]
    request_args: Optional[dict]
    additional_info: Optional[AdditionalInfo] = AdditionalInfo()
    referer: Optional[Union[str, bytes]]
    location: Optional[Union[str, bytes]]
    mail: Optional[SMTPMailField]


class LegacyTokenHistory(TokenHistory[LegacyTokenHit]):
    token_type: Literal[TokenTypes.LEGACY] = TokenTypes.LEGACY
    hits: List[LegacyTokenHit] = []
