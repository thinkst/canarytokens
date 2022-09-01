import socket

import pytest
from twisted.internet.testing import FakeDatagramTransport
from twisted.names import dns, error

from canarytokens import canarydrop, queries
from canarytokens.channel_dns import ChannelDNS, DNSServerFactory
from canarytokens.models import TokenTypes
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

switchboard = Switchboard()


@pytest.mark.parametrize(
    "query_string,q_type,expected_result_type",
    [
        # Not the Canarytokens domain
        (
            "google.com",
            dns.A,
            lambda x: isinstance(x.value, error.DNSQueryRefusedError),
        ),
        (None, dns.CNAME, lambda x: x == ([], [], [])),
        (None, dns.SOA, lambda x: x[0][0].type == dns.SOA),
        (None, dns.NS, lambda x: x[0][0].type == dns.NS),
        ("notatoken.127.0.0.1", dns.A, lambda x: x[0][0].type == dns.A),
        ("noexample.com", dns.A, lambda x: isinstance(x.value, error.DomainError)),
    ],
)
def test_query_types(setup_db, settings, query_string, q_type, expected_result_type):
    resolver = ChannelDNS(
        listen_domain=settings.LISTEN_DOMAIN,
        switchboard=switchboard,
        backend_scheme="http",
        backend_hostname="127.0.0.1",
        settings=settings,
    )
    # Make token so nxdomain lookup is tested.
    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=TokenTypes.ADOBE_PDF,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
        redirect_url="https://youtube.com",
    )
    queries.save_canarydrop(cd)
    query_string = query_string or settings.DOMAINS[0]
    if query_string == "noexample.com":
        query_string = f"{canarytoken.value()}.{query_string}"
    m = dns.Message()
    m.addQuery(query_string.encode(), type=q_type)
    query = m.queries[0]
    query_result = resolver.query(query=query, src_ip="1.2.1.1").result

    assert expected_result_type(query_result)


@pytest.mark.parametrize(
    "token_type",
    [
        TokenTypes.DNS,
        TokenTypes.LOG4SHELL,
    ],
)
def test_channel_dns_query(setup_db, settings, token_type):
    """
    Test ChannelDNS.
    """
    resolver = ChannelDNS(
        listen_domain=settings.LISTEN_DOMAIN,
        switchboard=switchboard,
        backend_scheme="http",
        backend_hostname="127.0.0.1",
        settings=settings,
    )
    canarytoken = Canarytoken()
    cd = canarydrop.Canarydrop(
        type=token_type,
        generate=True,
        alert_email_enabled=False,
        alert_email_recipient="email@test.com",
        alert_webhook_enabled=False,
        alert_webhook_url=None,
        canarytoken=canarytoken,
        memo="memo",
        browser_scanner_enabled=False,
    )
    queries.save_canarydrop(cd)

    if cd.type == TokenTypes.LOG4SHELL:
        expected_trigger_query: bytes = f"xhostName.L4J.{cd.get_hostname()}".encode()
    else:
        expected_trigger_query = cd.get_hostname().encode()
    m = dns.Message()
    m.addQuery(expected_trigger_query, type=dns.A)
    query = m.queries[0]
    query_result = resolver.query(query=query, src_ip="1.2.1.1").result
    response_header = query_result[0][0]

    assert response_header.type == dns.A
    assert response_header.name.name == query.name.name
    assert (
        socket.inet_ntoa(
            response_header.payload.address,
        )
        == settings.PUBLIC_IP
    )

    _ = queries.get_canarydrop(canarytoken)


@pytest.mark.asyncio(asyncio_mode="strict")
@pytest.mark.parametrize(
    "query, address",
    [
        (
            dns.Query(name="example.com", type=dns.A),
            ("2.2.2.4", "53"),
        ),
        (
            dns.Query(name="example.com", type=dns.MX),
            ("2.2.2.4", "53"),
        ),
        (
            dns.Query(name="example.com", type=dns.AAAA),
            ("2.2.2.4", "53"),
        ),
        (
            dns.Query(name="example.com", type=dns.A),
            ("2.2.2.4", "53"),
        ),
        (
            dns.Query(name="example.com", type=dns.SOA),
            ("2.2.2.4", "53"),
        ),
        (
            dns.Query(name="example.com", type=dns.MX),
            # Port is 0
            ("2.2.2.4", 0),
        ),
        (
            dns.Query(name="example.com", type=dns.MX),
            # Address is None
            None,
        ),
    ],
)
async def test_DNS_server_factory(query, address):

    proto = dns.DNSDatagramProtocol(controller=None)
    transport = FakeDatagramTransport()
    proto.makeConnection(transport)

    dns_factory = DNSServerFactory()

    dns_factory.protocol = proto

    message = dns.Message()
    message.queries = [query]
    message.timeReceived = 1
    # Test address is None. Not faking trans
    if address is None:
        with pytest.raises(AttributeError):
            deferred = dns_factory.handleQuery(
                message=message, protocol=proto, address=address
            )
    # Test port is 0
    elif address[1] == 0:
        deferred = dns_factory.handleQuery(
            message=message, protocol=proto, address=address
        )
        assert deferred is None
    else:
        deferred = dns_factory.handleQuery(
            message=message, protocol=proto, address=address
        )
        deferred.result
