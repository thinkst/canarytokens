from typing import List, Literal, Optional

from pydantic import ConstrainedStr

from canarytokens.constants import MSWORD_TEXT_SNIPPET_MAX_CHARACTERS
from canarytokens.msword import MSWORD_TEXT_SNIPPET_PLACEMENT_PLAINTEXT
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


class MsWordTextSnippet(ConstrainedStr):
    max_length = MSWORD_TEXT_SNIPPET_MAX_CHARACTERS


class MsWordDocumentTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD
    include_text_snippet: bool = False
    text_snippet: Optional[MsWordTextSnippet] = None
    text_snippet_placement: Literal["metadata", "plaintext"] = (
        MSWORD_TEXT_SNIPPET_PLACEMENT_PLAINTEXT
    )


class MsWordDocumentTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD


class MsWordDocumentTokenHit(TokenHit):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD


class MsWordDocumentTokenHistory(TokenHistory[MsWordDocumentTokenHit]):
    token_type: Literal[TokenTypes.MS_WORD] = TokenTypes.MS_WORD
    hits: List[MsWordDocumentTokenHit] = []


class DownloadMSWordRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.MSWORD] = DownloadFmtTypes.MSWORD


class DownloadMSWordResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.APPMSWORD] = (
        DownloadContentTypes.APPMSWORD
    )
    filename: str
    token: str
    auth: str
