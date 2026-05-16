from typing import List, Literal, TypedDict

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


class NPMPublishToken(TypedDict):
    token: str
    token_id: str
    package_name: str
    package_version: str


class NPMPublishTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.NPM_PUBLISH] = TokenTypes.NPM_PUBLISH


class NPMPublishTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.NPM_PUBLISH] = TokenTypes.NPM_PUBLISH
    npm_token: str
    npm_token_id: str
    npm_package_name: str
    npm_package_version: str


class NPMPublishTokenHit(TokenHit):
    token_type: Literal[TokenTypes.NPM_PUBLISH] = TokenTypes.NPM_PUBLISH
    npm_package_name: str
    npm_package_version: str


class NPMPublishTokenHistory(TokenHistory[NPMPublishTokenHit]):
    token_type: Literal[TokenTypes.NPM_PUBLISH] = TokenTypes.NPM_PUBLISH
    hits: List[NPMPublishTokenHit] = []


class DownloadNPMPublishRequest(TokenDownloadRequest):
    fmt: Literal[DownloadFmtTypes.NPM_PUBLISH] = DownloadFmtTypes.NPM_PUBLISH


class DownloadNPMPublishResponse(TokenDownloadResponse):
    contenttype: Literal[DownloadContentTypes.APPZIP] = DownloadContentTypes.APPZIP
    filename: str = "npm_publish_canary.zip"
    content: bytes
    token: str
    auth: str
