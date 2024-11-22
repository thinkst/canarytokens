import re
from base64 import b64decode
from typing import Optional
from twisted.web.http import Request

SAML_POST_ARG = b"SAMLResponse"


def prepare_request(request: Request) -> Optional[bytes]:
    return request.args.pop(SAML_POST_ARG, [None])[0]


def extract_identity(saml_request: bytes) -> Optional[str]:
    data = b64decode(saml_request).decode()

    SEARCH_PATTERN = re.compile(r"<saml2:NameID[^>]*>(.+)</saml2:NameID>")
    result = SEARCH_PATTERN.search(data)
    if result is None:
        return None

    email: str = result.groups()[0]
    return email
