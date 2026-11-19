# Webhook capture for tests

Webhook tests use the FastAPI capture service in `tests/webhook_capture.py`.
Each test gets a unique URL and its captures are deleted at teardown. The
existing integration tests still send real HTTP alerts and inspect their payloads.

## Local runs

Pytest starts the receiver on `127.0.0.1:8088` when a test needs it. Unit tests
need no additional receiver setup.

For integration tests, start the application using these targets instead of
the ordinary frontend/switchboard targets:

```sh
make frontend-test
make switchboard-test
```

Then run the tests as usual, for example from `tests/`:

```sh
uv run pytest integration/test_against_token_server.py -v
```

The test launchers allow the receiver's exact IP and origin for `/hooks/`
requests, with redirects disabled. Production startup and the shared production
SSRF validator are unchanged. The receiver fixture applies the same allowance
only for the duration of tests using it.

## Shared, containerized, or live runs

Start the receiver separately from the repository root:

```sh
uv run uvicorn tests.webhook_capture:create_app --factory --host 0.0.0.0 --port 8088
```

Set `TEST_WEBHOOK_URL` to its base URL as reachable by the application, and
optionally `TEST_WEBHOOK_API_URL` to its base URL as reachable by pytest. Setting
`TEST_WEBHOOK_URL` tells pytest to use that service instead of starting one.
For local services started by the test launchers, set the same URL in their
environment; private receivers must use a literal IP address.

For example, if application containers reach the test host at `172.18.0.1`:

```sh
export TEST_WEBHOOK_URL=http://172.18.0.1:8088
export TEST_WEBHOOK_API_URL=http://127.0.0.1:8088
```

Parallel pytest workers can share this separately started service: capture IDs
are unique across workers. Use one Uvicorn worker because capture storage is
in memory. Restarting the receiver clears its state.

For live runs using your own receiver, `LIVE=True` requires a publicly reachable
`TEST_WEBHOOK_URL`, normally behind HTTPS. Its `/captures/` API exposes captured
test payloads; restrict access to test runners at your reverse proxy/network.
Public hostnames use the normal production address validation.

## Windows CI live tests

The Windows CI job sets `TEST_WEBHOOK_BACKEND=webhook.site`, since it tests
against the remote Canarytokens deployment. No repository variables or hosted
receiver are required. This backend creates one webhook.site token per pytest
session and reuses it across tests; helpers filter deliveries by Canarytoken.
Token creation retries HTTP 429 responses at one-minute intervals, up to ten
attempts. Captures expire according to webhook.site's retention policy.

You can also select this backend explicitly for other live runs. Local tests
and Linux CI use the local receiver by default.
