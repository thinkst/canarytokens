from twisted.test import proto_helpers

from canarytokens.channel_input_mtls import MAX_STORED_BYTES, MAX_STORED_LINES, mTLS


def _mtls(transport=None):
    m = mTLS(
        factory=None,
        headers=lambda: b"Content-Type: application/json",
        bodies={
            "unauthorized": {},
            "forbidden": {"message": "{}"},
            "bad": {"message": "bad request"},
        },
    )
    if transport is not None:
        m.makeConnection(transport)
    return m


def test_line_flood_bounded_by_line_count():
    """One-byte lines are the cheap vector: 3 wire bytes buy a ~34 byte object,
    so a byte cap alone cannot bound the list. The line cap holds it."""
    m = _mtls()
    for _ in range(MAX_STORED_LINES * 5):
        m.lineReceived(b"X")
    assert len(m.lines) == MAX_STORED_LINES
    assert m.stored_byte_count == MAX_STORED_LINES


def test_line_flood_bounded_by_bytes():
    """The aggregate byte cap matches a kube-apiserver's header block limit
    (net/http DefaultMaxHeaderBytes, 1 MiB): lines stop being stored once
    the request reaches the size an apiserver would have rejected."""
    m = _mtls()
    line = b"X" * 2048
    for _ in range((MAX_STORED_BYTES // len(line)) * 2):
        m.lineReceived(line)
    assert len(m.lines) == MAX_STORED_BYTES // len(line)
    assert m.stored_byte_count == MAX_STORED_BYTES


def test_oversized_request_still_completes_and_closes():
    """An apiserver rejects an oversized request and closes; this channel
    answers with its own 400 and closes rather than holding a truncated
    request in memory forever. The request line survives the truncation."""
    m = _mtls(proto_helpers.StringTransport())
    m.lineReceived(b"GET /api/v1/namespaces HTTP/1.1")
    for i in range(MAX_STORED_LINES * 2):
        m.lineReceived(b"X-Pad-%d: %d" % (i, i))
    m.lineReceived(b"")
    assert m.transport.value().startswith(b"HTTP/1.1 400 Bad Request")
    assert len(m.lines) == MAX_STORED_LINES + 1
    assert m.stored_byte_count < MAX_STORED_BYTES


def test_normal_request_still_answered():
    """A kubectl-sized request (a handful of lines, well under a kilobyte)
    is buffered and answered exactly as before."""
    m = _mtls(proto_helpers.StringTransport())
    m.lineReceived(b"GET /version HTTP/1.1")
    m.lineReceived(b"Host: 127.0.0.1:6443")
    m.lineReceived(b"User-Agent: kubectl/v1.31.0")
    m.lineReceived(b"")
    assert m.transport.value().startswith(b"HTTP/1.1 400 Bad Request")
    assert len(m.lines) == 4
