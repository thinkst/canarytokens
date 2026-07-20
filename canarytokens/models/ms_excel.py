from typing import List, Literal, Optional
from pydantic import ConstrainedStr

from canarytokens.constants import MSEXCEL_TEXT_SNIPPET_MAX_CHARACTERS

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


class MsExcelTextSnippet(ConstrainedStr):
    max_length = MSEXCEL_TEXT_SNIPPET_MAX_CHARACTERS


class MsExcelDocumentTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.MS_EXCEL] = TokenTypes.MS_EXCEL
    include_text_snippet: bool = False
    text_snippet: Optional[MsExcelTextSnippet] = None


class MsExcelDocumentTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.MS_EXCEL] = TokenTypes.MS_EXCEL


class MsExcelDocumentTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MS_EXCEL] = TokenTypes.MS_EXCEL


class MsExcelDocumentTokenHistory(TokenHistory[MsExcelDocumentTokenHit]):
    token_type: Literal[TokenTypes.MS_EXCEL] = TokenTypes.MS_EXCEL
    hits: List[MsExcelDocumentTokenHit] = []


class DownloadMSExcelRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.MSEXCEL] = DownloadFmtTypes.MSEXCEL


class DownloadMSExcelResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.APPMSEXCELL] = (
        DownloadContentTypes.APPMSEXCELL
    )
    filename: str
    token: str
    auth: str
