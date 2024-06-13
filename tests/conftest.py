import contextlib
from ipaddress import IPv4Address
import logging
import os
import threading
import time
from distutils.util import strtobool
from pathlib import Path
from typing import Any, Generator, Optional
from unittest import mock

import pytest
from redis import StrictRedis
import requests
from requests import HTTPError
import uvicorn  # type: ignore
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import HttpUrl
from starlette.responses import JSONResponse

from canarytokens import kubeconfig
from canarytokens.channel_input_mtls import mTLS
from canarytokens.queries import (
    add_canary_domain,
    add_canary_nxdomain,
    add_canary_page,
    add_canary_path_element,
    get_certificate,
    save_certificate,
    save_kc_endpoint,
)
from canarytokens.redismanager import DB, KEY_KUBECONFIG_CERTS, KEY_KUBECONFIG_SERVEREP
from canarytokens.settings import FrontendSettings, Port, SwitchboardSettings

# TODO: Once webhooker can handle more / faster traffic these will get upped
# DESIGN: ngrok to get a basic webhook(er). This can be a lambda or a docker service.
#         main limitation is number of connections.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


@pytest.fixture(scope="function")
def webhook_receiver() -> Generator[str, None, None]:
    """
    Provides an alerting URL for tests.

    Returns:
       None: on teardown nothing is returned

    Yields:
         str: url to the alert endpoint
    """

    # acquire a URL and return it
    resp = requests.post("https://webhook.site/token")
    attempts = 1
    while resp.status_code == 429:  # too many requests
        time.sleep(6.1)  # webhook.site allows 10 per minute; sometimes we're too fast
        resp = requests.post("https://webhook.site/token")
        attempts += 1
        if attempts == 10:
            raise HTTPError(
                f"Failed to acquire a webhook after 10 attempts: {resp.status_code=}; {resp.content=}"
            )
    resp.raise_for_status()
    data = resp.json()
    uuid = data["uuid"]
    url = f"https://webhook.site/{uuid}"
    yield url
    # tear down
    # for webhook.site there's nothing to do; they'll delete in 7 days


@pytest.fixture(scope="function")
def aws_webhook_receiver() -> Generator[str, None, None]:
    """
    Stands up a simple web server to emulate the lambda that returns AWS keys

    Endpoints:
    /mock_aws_key/CreateUserAPITokens -> returns testing aws creds
    /mock_aws_key_broken/CreateUserAPITokens -> returns a 400

    Note: Debugging this web server you'll need rpdb.
    Returns:
       None: on teardown nothing is returned

    Yields:
         str: url to /
    """

    app = FastAPI()

    @app.get("/")
    def serve_aws_alert_endpoint(request: Request) -> JSONResponse:
        return JSONResponse(content={}, status_code=200)

    @app.get("/mock_aws_key/CreateUserAPITokens")
    def serve_aws_debug_token(request: Request) -> dict[str, Optional[str]]:
        """
        This provides a simple test endpoint that returns AWS creds
        in the same way the `CreateUserAPITokens` lambda does.
        """
        # TODO: loading settings here is likely no needed - should be not needed.
        frontend_settings = FrontendSettings(
            NXDOMAINS=["nxdomain.127.0.0.1"],
            PUBLIC_IP="10.0.1.3",
            DOMAINS=["127.0.0.1"],
            AWSID_URL=HttpUrl("https://not.using/in/tests", scheme="https"),
            AZURE_ID_TOKEN_URL=HttpUrl("https://not.using/in/tests", scheme="https"),
            AZURE_ID_TOKEN_AUTH="N/A=",
            SENTRY_DSN=HttpUrl("https://not.using/in/tests", scheme="https"),
            GOOGLE_API_KEY="N/A=",
        )
        mock_key = {
            "access_key_id": frontend_settings.TESTING_AWS_ACCESS_KEY_ID,
            "secret_access_key": frontend_settings.TESTING_AWS_SECRET_ACCESS_KEY,
            "region": frontend_settings.TESTING_AWS_REGION,
            "output": frontend_settings.TESTING_AWS_OUTPUT,
        }
        return mock_key

    @app.get("/mock_aws_key_broken/CreateUserAPITokens")
    def serve_aws_debug_token_broken(request: Request) -> JSONResponse:
        return JSONResponse(content={}, status_code=400)

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8087,
        log_level="info",
        limit_concurrency=10,
        timeout_keep_alive=0,
        backlog=5,
    )
    server = Server(config=config)
    with server.run_in_thread():
        yield f"http://{config.host}:{config.port}"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--runv3", action="store_true", default=False, help="run V3 tests")
    parser.addoption("--runv2", action="store_true", default=False, help="run V2 tests")


@pytest.fixture(scope="session")
def runv2(request: pytest.FixtureRequest) -> bool:
    return request.config.getoption("--runv2", False)


@pytest.fixture(scope="session")
def runv3(request: pytest.FixtureRequest) -> bool:
    return request.config.getoption("--runv3", False)


@pytest.fixture(scope="session")
def settings() -> SwitchboardSettings:
    return SwitchboardSettings(
        PUBLIC_DOMAIN="127.0.0.1",
        CHANNEL_HTTP_PORT=Port(8084),
        CHANNEL_SMTP_PORT=Port(25)
        if strtobool(os.getenv("LIVE", "FALSE"))
        else Port(2500),
        MAILGUN_DOMAIN_NAME="eu-mg.honeypdfs.com"
        if not os.getenv("CANARY_MAILGUN_DOMAIN_NAME")
        else os.getenv("CANARY_MAILGUN_DOMAIN_NAME"),
        MAILGUN_BASE_URL="https://api.eu.mailgun.net"
        if not os.getenv("CANARY_MAILGUN_DOMAIN_NAME")
        else os.getenv("CANARY_MAILGUN_BASE_URL"),
        SENTRY_DSN=HttpUrl("https://not.using/in/tests", scheme="https"),
        WG_PRIVATE_KEY_SEED="vk/GD+frlhve/hDTTSUvqpQ/WsQtioKAri0Rt5mg7dw=",
    )


@pytest.fixture(scope="session")
def fake_settings_for_aws_keys():
    """Used for unit tests that need TESTING_AWS...
    details.
    """
    return SwitchboardSettings(
        PUBLIC_DOMAIN="127.0.0.1",
        CHANNEL_HTTP_PORT=Port(8084),
        CHANNEL_SMTP_PORT=Port(25)
        if strtobool(os.getenv("LIVE", "FALSE"))
        else Port(2500),
        SENTRY_DSN=HttpUrl("https://not.using/in/tests", scheme="https"),
        WG_PRIVATE_KEY_SEED="vk/GD+frlhve/hDTTSUvqpQ/WsQtioKAri0Rt5mg7dw=",
    )


@pytest.fixture(scope="session", autouse=True)
def settings_env_vars() -> Generator[None, None, None]:
    """
    `app` from frontend/app.py is loaded by the test_frontend
    file and relative paths to `templates` differs. This ensures the
    `app` if launched by the testing harness has sensible defaults.
    """
    with mock.patch.dict(
        os.environ,
        {
            # "CANARY_STATIC_FILES_PATH": "templates/static",
            # "CANARY_TEMPLATES_PATH": "templates",
            "CANARY_TESTING_AWS_ACCESS_KEY_ID": "placeholder_key_id",
            "CANARY_TESTING_AWS_SECRET_ACCESS_KEY": "placeholder_secret_key",
            "CANARY_TESTING_AWS_REGION": "us-east-2",
            "CANARY_TESTING_AWS_OUTPUT": "json",
        },
        clear=False,
    ):
        yield


@pytest.fixture(scope="session")
def frontend_settings() -> FrontendSettings:
    return FrontendSettings(
        NXDOMAINS=["nx.127.0.0.1"],
        PUBLIC_IP="127.0.0.1",  # "10.0.1.3",
        DOMAINS=["127.0.0.1"],
        SENTRY_DSN=HttpUrl("https://not.using/in/tests", scheme="https://"),
        TEMPLATES_PATH="../templates",
        STATIC_FILES_PATH="../templates/static",
        STATIC_FILES_APPLICATION_SUB_PATH="/resources",
        STATIC_FILES_APPLICATION_INTERNAL_NAME="resources",
        WEB_IMAGE_UPLOAD_PATH="../uploads",
        AWSID_URL=HttpUrl("https://overwrit.e/from/outside", scheme="https"),
        TESTING_AWS_ACCESS_KEY_ID="placeholder_key_id",
        TESTING_AWS_SECRET_ACCESS_KEY="placeholder_secret_key",
        GOOGLE_API_KEY="nothing_here",
    )


@pytest.fixture(scope="session")
def setup_db_connection_only(settings: SwitchboardSettings):
    redis_hostname = "localhost" if strtobool(os.getenv("CI", "False")) else "redis"
    DB.set_db_details(hostname=redis_hostname, port=6379)


@pytest.fixture(scope="function", autouse=False)
def setup_db(  # noqa: C901
    settings: SwitchboardSettings, frontend_settings: FrontendSettings
) -> Generator[Any, Any, Optional[StrictRedis]]:
    redis_hostname = "localhost" if strtobool(os.getenv("CI", "False")) else "redis"
    DB.set_db_details(hostname=redis_hostname, port=6379)
    # Kubeconfig token needs a client cert in redis.
    # DESIGN: This is a red flag! Will need a refactor at some point.
    # Get or generate the client CA
    try:
        client_ca = get_certificate(kubeconfig.ClientCA)
    except LookupError:
        client_ca = mTLS.generate_new_ca(
            username="kubernetes-ca",
        )
        save_certificate(kubeconfig.ClientCA, client_ca)
    # Get or generate the server CA
    try:
        server_ca = get_certificate(kubeconfig.ServerCA)
    except LookupError:
        server_ca = mTLS.generate_new_ca(
            username="kubernetes-ca",
        )
        save_certificate(kubeconfig.ServerCA, server_ca)
    # Get or generate the server cert, issued by server CA
    try:
        server_cert = get_certificate(kubeconfig.ServerCert)
    except LookupError:
        server_cert = mTLS.generate_new_certificate(
            ca_redis_key=kubeconfig.ServerCA,
            username="kubernetes-ca",
            ip=IPv4Address(frontend_settings.PUBLIC_IP),
            is_server_cert=True,
        )
        save_certificate(kubeconfig.ServerCert, server_cert)
    db = DB.get_db()
    prefixes_to_persist = [KEY_KUBECONFIG_CERTS, KEY_KUBECONFIG_SERVEREP]
    for key in db.scan_iter():
        if not any(key.startswith(key_prefix) for key_prefix in prefixes_to_persist):
            db.delete(key)

    save_kc_endpoint(
        frontend_settings.DOMAINS[0],
        settings.CHANNEL_MTLS_KUBECONFIG_PORT,
    )

    add_canary_domain(frontend_settings.DOMAINS[0])
    add_canary_nxdomain(frontend_settings.NXDOMAINS[0])
    add_canary_page("post.jsp")
    add_canary_path_element("tags")

    yield db

    for key in db.scan_iter():
        if not any(key.startswith(key_prefix) for key_prefix in prefixes_to_persist):
            db.delete(key)
    # DESIGN: canarytokens needs these and adds them on startup.
    #         Tests should ensure we don't interfere too much.
    #         Remove dependence on redis as a shared global.
    add_canary_domain(frontend_settings.DOMAINS[0])
    add_canary_nxdomain(frontend_settings.NXDOMAINS[0])
    add_canary_page("post.jsp")
    add_canary_path_element("tags")


@pytest.fixture(scope="session", autouse=False)
def test_client(settings_env_vars: None) -> Generator[TestClient, None, None]:
    from frontend.app import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def set_template_env_for_tests():
    from canarytokens import tokens

    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    tokens.set_template_env(dir_path / "../templates")


@pytest.fixture(scope="session")
def clean_uploads_dir():
    """Removes all files folders and even the `/uploads` dir
    after tests complete.
    """
    yield
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    uploads_dir = dir_path / "../uploads"
    for image_dir in uploads_dir.glob("*"):
        [o.unlink(missing_ok=True) for o in image_dir.glob("*.*")]
        image_dir.rmdir()
    if uploads_dir.exists():
        uploads_dir.rmdir()
