__version__ = "1.0.0"

from requests import utils
from requests.models import Request, Response, PreparedRequest
from requests.status_codes import codes
from requests.exceptions import (
    RequestException,
    Timeout,
    URLRequired,
    TooManyRedirects,
    HTTPError,
    ConnectionError,
)

from .adapters import ValidatingHTTPAdapter
from .api import *
from .addrvalidator import AddrValidator
from .exceptions import UnacceptableAddressException
