import contextlib
from ipaddress import IPv4Address
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Generator, Optional
from unittest import mock
from uuid import uuid4

import pytest
from redis import StrictRedis
import requests
import uvicorn  # type: ignore
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from canarytokens import kubeconfig
from canarytokens.channel_input_mtls import mTLS
from canarytokens.queries import (
    add_canary_domain,
    add_canary_nxdomain,
    add_canary_page,
    add_canary_image_page,
    add_canary_path_element,
    get_certificate,
    save_certificate,
    save_kc_endpoint,
)
from canarytokens.redismanager import DB, KEY_KUBECONFIG_CERTS, KEY_KUBECONFIG_SERVEREP
from canarytokens.settings import FrontendSettings, Port, SwitchboardSettings
from canarytokens.utils import strtobool
from tests.webhook_capture import (
    allow_capture_delivery,
    capture_api_url,
    create_app,
    create_webhook_site_url,
)

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
            deadline = time.monotonic() + 10
            while not self.started:
                if not thread.is_alive() or time.monotonic() >= deadline:
                    raise RuntimeError("Test HTTP server failed to start")
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


@pytest.fixture(scope="session")
def webhook_capture_server() -> Generator[str, None, None]:
    external_url = os.getenv("TEST_WEBHOOK_URL")
    if external_url:
        yield external_url.rstrip("/")
        return
    if strtobool(os.getenv("LIVE", "False")):
        pytest.fail("LIVE tests require TEST_WEBHOOK_URL pointing to an owned receiver")
    config = uvicorn.Config(create_app(), host="127.0.0.1", port=8088)
    with Server(config).run_in_thread():
        yield "http://127.0.0.1:8088"


@pytest.fixture(scope="function")
def webhook_receiver(request, monkeypatch) -> Generator[str, None, None]:
    from canarytokens import advocate

    backend = os.getenv("TEST_WEBHOOK_BACKEND", "local")
    if backend == "webhook.site":
        yield request.getfixturevalue("webhook_site_receiver")
        return
    if backend != "local":
        pytest.fail(f"Unknown TEST_WEBHOOK_BACKEND: {backend}")
    webhook_capture_server = request.getfixturevalue("webhook_capture_server")
    monkeypatch.setattr(
        advocate, "post", allow_capture_delivery(advocate.post, webhook_capture_server)
    )
    url = f"{webhook_capture_server}/hooks/{uuid4().hex}"
    api_url = capture_api_url(url)
    requests.post(api_url, timeout=5).raise_for_status()
    try:
        yield url
    finally:
        requests.delete(api_url, timeout=5).raise_for_status()


@pytest.fixture(scope="session")
def webhook_site_receiver() -> str:
    return create_webhook_site_url()


@pytest.fixture(scope="function")
def aws_webhook_receiver() -> Generator[str, None, None]:
    """
    Stands up a simple web server to emulate the lambda that returns AWS keys

    Endpoints:
    /mock_aws_key/LinkAWSIDTokenUserToCanaryConsole -> returns testing aws creds
    /mock_aws_key_broken/LinkAWSIDTokenUserToCanaryConsole -> returns a 400

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

    @app.get("/mock_aws_key/LinkAWSIDTokenUserToCanaryConsole")
    def serve_aws_debug_token(
        request: Request,
    ) -> dict[str, Optional[str]]:
        """
        This provides a simple test endpoint that returns AWS creds
        in the same way the `LinkAWSIDTokenUserToCanaryConsole` lambda does.
        """

        # TODO: loading settings here is likely no needed - should be not needed.
        frontend_settings = FrontendSettings(
            NXDOMAINS=["nxdomain.127.0.0.1"],
            PUBLIC_IP="10.0.1.3",
            DOMAINS=["127.0.0.1"],
            AWSID_URL="https://not.using/in/tests",
            AWSID_AUTH="N/A=",
            AZURE_ID_TOKEN_URL="https://not.using/in/tests",
            AZURE_ID_TOKEN_AUTH="N/A=",
            SENTRY_DSN="https://not.using/in/tests",
            GOOGLE_API_KEY="N/A=",
        )
        mock_key = {
            "access_key_id": frontend_settings.TESTING_AWS_ACCESS_KEY_ID,
            "secret_access_key": frontend_settings.TESTING_AWS_SECRET_ACCESS_KEY,
            "username": "awsid-test-user",
            "region": frontend_settings.TESTING_AWS_REGION,
            "output": frontend_settings.TESTING_AWS_OUTPUT,
        }
        return mock_key

    @app.get("/mock_aws_key_broken/LinkAWSIDTokenUserToCanaryConsole")
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


@pytest.fixture(scope="session")
def settings() -> SwitchboardSettings:
    return SwitchboardSettings(
        PUBLIC_DOMAIN="127.0.0.1",
        CHANNEL_HTTP_PORT=Port(8084),
        CHANNEL_SMTP_PORT=(
            Port(25) if strtobool(os.getenv("LIVE", "FALSE")) else Port(2500)
        ),
        MAILGUN_DOMAIN_NAME=(
            "eu-mg.honeypdfs.com"
            if not os.getenv("CANARY_MAILGUN_DOMAIN_NAME")
            else os.getenv("CANARY_MAILGUN_DOMAIN_NAME")
        ),
        MAILGUN_BASE_URL=(
            "https://api.eu.mailgun.net"
            if not os.getenv("CANARY_MAILGUN_DOMAIN_NAME")
            else os.getenv("CANARY_MAILGUN_BASE_URL")
        ),
        SENTRY_DSN="https://not.using/in/tests",
        WG_PRIVATE_KEY_SEED="vk/GD+frlhve/hDTTSUvqpQ/WsQtioKAri0Rt5mg7dw=",
        LAMBDA_AWS_CRED_REPORT_AUTH="test_auth_value",
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
        SENTRY_DSN="https://not.using/in/tests",
        TEMPLATES_PATH="../templates",
        STATIC_FILES_PATH="../templates/static",
        STATIC_FILES_APPLICATION_SUB_PATH="/resources",
        STATIC_FILES_APPLICATION_INTERNAL_NAME="resources",
        WEB_IMAGE_UPLOAD_PATH="../uploads",
        AWSID_URL="https://overwrit.e/from/outside",
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
    add_canary_image_page("photo1.jpg")
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
    add_canary_image_page("photo1.jpg")
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
