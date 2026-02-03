import pytest
from canarytokens.saml import extract_identity, prepare_request
from twisted.web.http import Request
from twisted.web.test.requesthelper import DummyChannel

with open("data/sample_saml_data.txt") as f:
    raw_text = f.read()


@pytest.mark.parametrize(
    "args, expected_identity",
    [
        (
            {b"SAMLResponse": [raw_text.encode()]},
            "tokens-testing@thinkst.com",
        )
    ],
)
def test_extract_identity(args, expected_identity):
    request = Request(channel=DummyChannel())
    request.args = args
    prepared_request = prepare_request(request)
    extracted_identity = extract_identity(prepared_request)
    assert extracted_identity == expected_identity
