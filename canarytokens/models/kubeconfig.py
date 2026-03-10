from typing import Any, List, Literal
from .common import TokenHistory, TokenHit, TokenRequest, TokenResponse, TokenTypes


class KubeconfigTokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.KUBECONFIG] = TokenTypes.KUBECONFIG


class KubeconfigTokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.KUBECONFIG] = TokenTypes.KUBECONFIG
    kubeconfig: str

    def __init__(__pydantic_self__, **data: Any) -> None:
        scheme = "http"
        host = "hostname.com"
        token = "random1token2string4test5"

        if "Hostname" in data:  # pragma: no cover
            data["hostname"] = data.pop("Hostname")
        if "Url_components" in data:  # pragma: no cover
            data["url_components"] = data.pop("Url_components")
        if "Url" in data and data["Url"]:  # pragma: no cover
            data["token_url"] = data.pop("Url")

        if data.get("hostname", "") == "":  # pragma: no cover
            data["hostname"] = "{token}.{host}".format(token=token, host=host)

        if data.get("url_components", "") == "":  # pragma: no cover
            data["url_components"] = None

        if data.get("token_url", "") == "":  # pragma: no cover
            data["token_url"] = "{scheme}://{host}/static/{token}/post.jsp".format(
                scheme=scheme, host=host, token=token
            )

        super().__init__(**data)


class KubeconfigTokenHit(TokenHit):
    token_type: Literal[TokenTypes.KUBECONFIG] = TokenTypes.KUBECONFIG
    location: str


class KubeconfigTokenHistory(TokenHistory[KubeconfigTokenHit]):
    token_type: Literal[TokenTypes.KUBECONFIG] = TokenTypes.KUBECONFIG
    hits: List[KubeconfigTokenHit] = []
