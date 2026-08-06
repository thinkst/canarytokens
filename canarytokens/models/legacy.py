from typing import List, Literal, Optional, Union

from canarytokens.models.smtp import SMTPMailField
from .common import AdditionalInfo, TokenHistory, TokenHit, TokenTypes


class LegacyTokenHit(TokenHit):
    token_type: Literal[TokenTypes.LEGACY] = TokenTypes.LEGACY
    src_data: Optional[dict] = None
    request_headers: Optional[dict] = None
    request_args: Optional[dict] = None
    additional_info: Optional[AdditionalInfo] = AdditionalInfo()
    referer: Optional[Union[str, bytes]] = None
    location: Optional[Union[str, bytes]] = None
    mail: Optional[SMTPMailField] = None


class LegacyTokenHistory(TokenHistory[LegacyTokenHit]):
    token_type: Literal[TokenTypes.LEGACY] = TokenTypes.LEGACY
    hits: List[LegacyTokenHit] = []
