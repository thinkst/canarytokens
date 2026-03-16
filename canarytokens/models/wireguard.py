from typing import List, Literal, TypedDict
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class WireguardSrcData(TypedDict):
    src_port: int
    server_public_key: bytes
    client_public_key: bytes
    session_index: int


class WireguardTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.WIREGUARD] = TokenTypes.WIREGUARD


class WireguardTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.WIREGUARD] = TokenTypes.WIREGUARD
    wg_conf: str
    qr_code: str


class WireguardTokenHit(TokenHit):
    token_type: Literal[TokenTypes.WIREGUARD] = TokenTypes.WIREGUARD
    src_data: WireguardSrcData


class WireguardTokenHistory(TokenHistory[WireguardTokenHit]):
    token_type: Literal[TokenTypes.WIREGUARD] = TokenTypes.WIREGUARD
    hits: List[WireguardTokenHit] = []
