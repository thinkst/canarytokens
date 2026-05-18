from canarytokens import queries
from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def test_upstream_tor_exit_nodes_list(setup_db):
    # Test the real upstream exactly once to not overload it with requests
    # originating from CI, but still be alerted if it stops working

    queries.clear_tor_exit_nodes()
    assert queries.is_tor_relay('8.8.8.8') is None

    ips = yield queries.update_tor_exit_nodes()
    assert len(ips) > 10
    for ip in ips:
        assert queries.is_tor_relay(ip) is True

    assert queries.is_tor_relay('8.8.8.8') is False
