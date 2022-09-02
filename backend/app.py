# Design: An API same as before for testing.This could remain separate
# or get pulled into the v3 frontend.
# RFC - V3
# Keeping a backend separate has a few advantages:
#               1) Offer api based token creation.
#               2) deferred porting frontend and token creation at the same time.
#

import base64
import datetime
import errno
import hashlib
import os
import textwrap
from base64 import b64decode
from distutils.util import strtobool
from functools import singledispatch
from pathlib import Path
from typing import Any, Optional

import requests
import segno
import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import APIKeyQuery
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl, parse_obj_as
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration

import canarytokens
from canarytokens import kubeconfig, queries
from canarytokens import wireguard as wg
from canarytokens.authenticode import make_canary_authenticode_binary
from canarytokens.awskeys import get_aws_key
from canarytokens.canarydrop import Canarydrop
from canarytokens.exceptions import CanarydropAuthFailure
from canarytokens.models import (
    AnyDownloadRequest,
    AnySettingsRequest,
    AnyTokenRequest,
    AnyTokenResponse,
    AWSKeyTokenRequest,
    AWSKeyTokenResponse,
    ClonedWebTokenRequest,
    ClonedWebTokenResponse,
    CustomBinaryTokenRequest,
    CustomBinaryTokenResponse,
    CustomImageTokenRequest,
    CustomImageTokenResponse,
    DNSTokenRequest,
    DNSTokenResponse,
    DownloadAWSKeysRequest,
    DownloadAWSKeysResponse,
    DownloadIncidentListCSVRequest,
    DownloadIncidentListCSVResponse,
    DownloadIncidentListJsonRequest,
    DownloadIncidentListJsonResponse,
    DownloadKubeconfigRequest,
    DownloadKubeconfigResponse,
    DownloadMSExcelRequest,
    DownloadMSExcelResponse,
    DownloadMSWordRequest,
    DownloadMSWordResponse,
    DownloadMySQLRequest,
    DownloadMySQLResponse,
    DownloadPDFRequest,
    DownloadPDFResponse,
    DownloadQRCodeRequest,
    DownloadQRCodeResponse,
    DownloadSplackApiRequest,
    DownloadSplackApiResponse,
    DownloadZipRequest,
    DownloadZipResponse,
    FastRedirectTokenRequest,
    FastRedirectTokenResponse,
    KubeconfigTokenRequest,
    KubeconfigTokenResponse,
    Log4ShellTokenRequest,
    Log4ShellTokenResponse,
    MsExcelDocumentTokenRequest,
    MsExcelDocumentTokenResponse,
    MsWordDocumentTokenRequest,
    MsWordDocumentTokenResponse,
    MySQLTokenRequest,
    MySQLTokenResponse,
    PDFTokenRequest,
    PDFTokenResponse,
    QRCodeTokenRequest,
    QRCodeTokenResponse,
    SettingsResponse,
    SlowRedirectTokenRequest,
    SlowRedirectTokenResponse,
    SMTPTokenRequest,
    SMTPTokenResponse,
    SQLServerTokenRequest,
    SQLServerTokenResponse,
    SvnTokenRequest,
    SvnTokenResponse,
    TokenTypes,
    WebBugTokenRequest,
    WebBugTokenResponse,
    WindowsDirectoryTokenRequest,
    WindowsDirectoryTokenResponse,
    WireguardTokenRequest,
    WireguardTokenResponse,
)
from canarytokens.msexcel import make_canary_msexcel
from canarytokens.msword import make_canary_msword
from canarytokens.mysql import make_canary_mysql_dump
from canarytokens.pdfgen import make_canary_pdf
from canarytokens.queries import (
    add_canary_domain,
    add_canary_google_api_key,
    add_canary_nxdomain,
    add_canary_page,
    add_canary_path_element,
    get_all_canary_domains,
    get_all_canary_sites,
    remove_canary_domain,
    save_canarydrop,
    validate_webhook,
)
from canarytokens.redismanager import DB
from canarytokens.settings import BackendSettings, Settings
from canarytokens.tokens import Canarytoken
from canarytokens.utils import get_deployed_commit_sha
from canarytokens.ziplib import make_canary_zip

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))

backend_settings = BackendSettings(_env_file=dir_path / "backend.env")
switchboard_settings = Settings(
    _env_file=dir_path / backend_settings.SWITCHBOARD_SETTINGS_PATH
)
if switchboard_settings.USING_NGINX:
    canary_http_channel = f"http://{switchboard_settings.DOMAINS[0]}"
else:
    canary_http_channel = f"http://{switchboard_settings.DOMAINS[0]}:{switchboard_settings.CHANNEL_HTTP_PORT}"

sentry_sdk.init(
    dsn=backend_settings.SENTRY_DSN,
    environment=backend_settings.SENTRY_ENVIRONMENT,
    traces_sample_rate=0.2,
    integrations=[
        RedisIntegration(),
        FastApiIntegration(),
    ],
    release=canarytokens.utils.get_deployed_commit_sha(),
)


tags_metadata = [
    {
        "name": "Create Canarytokens",
        "description": "Endpoint to create Canarytokens.",
        "externalDocs": {
            "description": "All Canarytoken types are described here",
            "url": "https://docs.canarytokens.org/guide/",
        },
    },
]


app = FastAPI(
    title=backend_settings.API_APP_TITLE,
    version=canarytokens.__version__,
    openapi_tags=tags_metadata,
)
app.mount(
    backend_settings.STATIC_FILES_APPLICATION_SUB_PATH,
    StaticFiles(directory=backend_settings.STATIC_FILES_PATH),
    name=backend_settings.STATIC_FILES_APPLICATION_INTERNAL_NAME,
)
templates = Jinja2Templates(directory=backend_settings.TEMPLATES_PATH)

if backend_settings.BACKEND_HOSTNAME != "127.0.0.1":
    # Add sentry when running on a domain.
    app.add_middleware(SentryAsgiMiddleware)


def capture_exception(error: BaseException, context: tuple[str, Any]):
    with sentry_sdk.configure_scope() as scope:
        scope.set_context(*context)
        sentry_sdk.capture_exception(error)


auth_key = APIKeyQuery(name="auth", description="Auth key for a token")


async def _parse_for_x(request: Request, expected_type: Any) -> Any:
    if request.headers.get("Content-Type", "application/json") == "application/json":
        if all([o in request.query_params.keys() for o in ["token", "auth"]]):
            data = dict(request.query_params.items())
        else:
            data = await request.json()
    elif "application/x-www-form-urlencoded" in request.headers["Content-Type"]:
        data = await request.form()
    else:
        raise HTTPException(status_code=422, detail="Invalid data")
    return parse_obj_as(expected_type, data)


async def parse_for_settings(request: Request) -> AnySettingsRequest:
    return await _parse_for_x(request, AnySettingsRequest)


async def parse_for_download(request: Request) -> AnyDownloadRequest:
    return await _parse_for_x(request, AnyDownloadRequest)


async def authorise_token_access(request: Request):
    """
    Intercept a request and check that it contains a
    valid `token`, `auth` pair.

    Args:
        request (Request): Incoming a request.

    Raises:
        HTTPException: 403 errors raised when auth fails.
    """
    if request.headers.get("Content-Type", "application/json") == "application/json":
        if all([o in request.query_params.keys() for o in ["token", "auth"]]):
            data = dict(request.query_params.items())
        else:
            data = await request.json()
    elif "multipart/form-data" in request.headers["Content-Type"]:
        data = dict(await request.form())
    elif "application/x-www-form-urlencoded" in request.headers["Content-Type"]:
        data = dict(await request.form())
    else:
        raise HTTPException(status_code=403, detail="Requires `auth` and `token`")
    get_canarydrop_from_auth(token=data["token"], auth=data["auth"])


def get_canarydrop_from_auth(token: str, auth: str = Security(auth_key)):
    try:
        canarydrop = queries.get_canarydrop_from_auth(token=token, auth=auth)
    except CanarydropAuthFailure:
        raise HTTPException(
            status_code=403, detail="Token not found. Invalid `auth` and `token` pair."
        )
    return canarydrop


@app.on_event("startup")
def startup_event():
    redis_hostname = "localhost" if strtobool(os.getenv("CI", "False")) else "redis"
    DB.set_db_details(hostname=redis_hostname, port=6379)
    remove_canary_domain()
    remove_canary_domain()

    add_canary_domain(domain=switchboard_settings.LISTEN_DOMAIN)
    add_canary_google_api_key(backend_settings.GOOGLE_API_KEY)
    add_canary_nxdomain(domain=switchboard_settings.NXDOMAINS[0])
    add_canary_path_element(path_element="stuff")
    add_canary_page("payments.js")


@app.get("/", response_class=RedirectResponse, status_code=302)
async def redirect_to_generate_page():
    return "/generate"


@app.get(
    "/generate",
    tags=["Canarytokens generate page"],
    response_class=HTMLResponse,
)
def generate_page(request: Request) -> HTMLResponse:
    sites_len = len(get_all_canary_sites())
    now = datetime.datetime.now()
    generate_template_params = {
        "request": request,
        "build_id": get_deployed_commit_sha(),
        "sites_len": sites_len,
        "now": now,
    }
    return templates.TemplateResponse("generate_new.html", generate_template_params)


@app.post(
    "/generate",
    tags=["Create Canarytokens"],
)
async def generate(request: Request) -> AnyTokenResponse:
    """
    Whatt
    """
    if request.headers.get("Content-Type", "application/json") == "application/json":
        token_request_details = parse_obj_as(AnyTokenRequest, await request.json())
    else:
        # Need a mutable copy of the form data
        token_request_form = dict(await request.form())
        token_request_form["token_type"] = token_request_form.pop(
            "type", token_request_form.get("token_type", None)
        )
        token_request_details = parse_obj_as(AnyTokenRequest, token_request_form)

    if token_request_details.webhook_url:
        try:
            validate_webhook(
                token_request_details.webhook_url, token_request_details.token_type
            )
        except requests.exceptions.HTTPError:
            raise HTTPException(status_code=400, detail="Failed to validate webhook")
        except requests.exceptions.ConnectTimeout:
            raise HTTPException(
                status_code=400, detail="Failed to validate webhook - timed out."
            )
    # TODO: refactor this. KUBECONFIG token creates it's own token
    # value and cannot follow same path as before.
    if token_request_details.token_type == TokenTypes.KUBECONFIG:
        token_value, kube_config = kubeconfig.get_kubeconfig()
        canarytoken = Canarytoken(value=token_value)
    else:
        kube_config = None
        canarytoken = Canarytoken()
    canarydrop = Canarydrop(
        type=token_request_details.token_type,
        alert_email_enabled=True,
        alert_email_recipient=token_request_details.email,
        alert_webhook_enabled=True,
        alert_webhook_url=token_request_details.webhook_url,
        canarytoken=canarytoken,
        memo=token_request_details.memo,
        browser_scanner_enabled=False,
        # Drop details to fullfil the tokens promise.
        # TODO: move all token type specific canary drop
        #       attribute setting into `create_response`
        #       which is already doing the type dispatch for us.
        kubeconfig=kube_config,
        redirect_url=getattr(token_request_details, "redirect_url", None),
        clonedsite=getattr(token_request_details, "clonedsite", None),
        sql_server_sql_action=getattr(
            token_request_details, "sql_server_sql_action", None
        ),
        sql_server_table_name=getattr(
            token_request_details, "sql_server_table_name", None
        ),
        sql_server_view_name=getattr(
            token_request_details, "sql_server_view_name", None
        ),
        sql_server_function_name=getattr(
            token_request_details, "sql_server_function_name", None
        ),
        sql_server_trigger_name=getattr(
            token_request_details, "sql_server_trigger_name", None
        ),
        # TODO: Move this into the create_response - same for much of what is done above.
        wg_key=wg.generateCanarytokenPrivateKey(
            canarytoken.value(),
            wg_private_key_seed=switchboard_settings.WG_PRIVATE_KEY_SEED,
            wg_private_key_n=switchboard_settings.WG_PRIVATE_KEY_N,
        )
        if token_request_details.token_type == TokenTypes.WIREGUARD
        else None,
    )

    # add generate random hostname an token
    canarydrop.token_url = canarydrop.get_url([canary_http_channel])
    canarydrop.generated_hostname = canarydrop.get_hostname()

    save_canarydrop(canarydrop)

    return create_response(token_request_details, canarydrop)


@app.get(
    "/manage",
    tags=["Manage Canarytokens"],
    response_class=HTMLResponse,
    dependencies=[Depends(authorise_token_access)],
)
async def manage_page_get(
    request: Request, canarydrop: Canarydrop = Depends(get_canarydrop_from_auth)
) -> HTMLResponse:

    manage_template_params = {
        "request": request,
        "canarydrop": canarydrop,
        "API_KEY": queries.get_canary_google_api_key(),
        "now": datetime.datetime.now(),
        "public_ip": switchboard_settings.PUBLIC_IP,
        "wg_private_key_seed": switchboard_settings.WG_PRIVATE_KEY_SEED,
        "wg_private_key_n": switchboard_settings.WG_PRIVATE_KEY_N,
    }

    if canarydrop.type == TokenTypes.WIREGUARD:
        wg_conf = wg.clientConfig(
            canarydrop.wg_key,
            switchboard_settings.PUBLIC_IP,
            switchboard_settings.WG_PRIVATE_KEY_SEED,
            switchboard_settings.WG_PRIVATE_KEY_N,
        )
        qr_code = segno.make(wg_conf).png_data_uri(scale=2)
        manage_template_params["wg_conf"] = wg_conf
        manage_template_params["wg_qr_code"] = qr_code
    elif canarydrop.type == TokenTypes.QR_CODE:
        qr_code = segno.make(canarydrop.token_url).png_data_uri(scale=5)
        manage_template_params["qr_code"] = qr_code

    return templates.TemplateResponse("manage_new.html", manage_template_params)


@app.get(
    "/history",
    tags=["Canarytokens History"],
    response_class=HTMLResponse,
    dependencies=[Depends(authorise_token_access)],
)
async def history_page_get(
    request: Request, canarydrop: Canarydrop = Depends(get_canarydrop_from_auth)
) -> HTMLResponse:

    triggered_list = canarydrop.format_triggered_details_of_history_page()
    triggered_list = jsonable_encoder(triggered_list)
    # TODO: history html expects v2 shaped data.
    #       Remove this when html is updated.
    canarydrop_dict = canarydrop.dict()
    canarydrop_dict["triggered_list"] = triggered_list
    history_template_params = {
        "request": request,
        "canarydrop": canarydrop_dict,
        "API_KEY": queries.get_canary_google_api_key(),
        "now": datetime.datetime.now(),
    }

    return templates.TemplateResponse("history.html", history_template_params)


@app.post(
    "/settings",
    tags=["Canarytokens Settings"],
    dependencies=[Depends(authorise_token_access)],
)
async def settings_post(
    settings_request: AnySettingsRequest = Depends(parse_for_settings),
) -> SettingsResponse:
    canarydrop = queries.get_canarydrop_from_auth(
        token=settings_request.token, auth=settings_request.auth
    )
    if canarydrop.apply_settings_change(setting_request=settings_request):
        return JSONResponse({"message": "success"})
    else:
        return JSONResponse({"message": "failure"}, status_code=400)


@app.get(
    "/download",
    tags=["Canarytokens Downloads"],
    dependencies=[Depends(authorise_token_access)],
)
async def download(
    download_request: AnyDownloadRequest = Depends(parse_for_download),
) -> Response:
    """
    Given `AnyDownloadRequest` a canarydrop is retrieved and the token
    artifact or hit information is returned.
    """
    canarydrop = queries.get_canarydrop_from_auth(
        token=download_request.token, auth=download_request.auth
    )
    return create_download_response(download_request, canarydrop=canarydrop)


@singledispatch
def create_download_response(download_request_details, canarydrop: Canarydrop):
    """"""
    raise NotImplementedError(
        f"DownloadRequest {download_request_details} not supported."
    )


@create_download_response.register
def _(
    download_request_details: DownloadMSWordRequest, canarydrop: Canarydrop
) -> Response:

    return DownloadMSWordResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=make_canary_msword(
            canarydrop.token_url,
            template=Path(backend_settings.TEMPLATES_PATH) / "template.docx",
        ),
        filename=f"{canarydrop.canarytoken.value()}.docx",
    )


@create_download_response.register
def _(download_request_details: DownloadZipRequest, canarydrop: Canarydrop) -> Response:
    hostname = f"{canarydrop.canarytoken.value()}.{switchboard_settings.LISTEN_DOMAIN}"
    windows_dir_content = make_canary_zip(hostname)

    return DownloadZipResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=windows_dir_content,
        filename=f"{canarydrop.canarytoken.value()}.zip",
    )


@create_download_response.register
def _(
    download_request_details: DownloadMSExcelRequest, canarydrop: Canarydrop
) -> Response:

    return DownloadMSExcelResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=make_canary_msexcel(
            canarydrop.token_url,
            template=Path(backend_settings.TEMPLATES_PATH) / "template.xlsx",
        ),
        filename=f"{canarydrop.canarytoken.value()}.xlsx",
    )


@create_download_response.register
def _(download_request_details: DownloadPDFRequest, canarydrop: Canarydrop) -> Response:

    return DownloadPDFResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=make_canary_pdf(
            hostname=canarydrop.get_hostname(nxdomain=True).encode(),
            template=Path(backend_settings.TEMPLATES_PATH) / "template.pdf",
        ),
        filename=f"{canarydrop.canarytoken.value()}.pdf",
    )


@create_download_response.register
def _(
    download_request_details: DownloadIncidentListJsonRequest, canarydrop: Canarydrop
) -> Response:

    json_content = canarydrop.triggered_details.json()

    return DownloadIncidentListJsonResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=json_content,
        filename=f"{canarydrop.canarytoken.value()}.json",
    )


@create_download_response.register
def _(
    download_request_details: DownloadMySQLRequest, canarydrop: Canarydrop
) -> Response:

    return DownloadMySQLResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=make_canary_mysql_dump(
            mysql_usage=Canarydrop.generate_mysql_usage(
                token=canarydrop.canarytoken.value(),
                domain=switchboard_settings.LISTEN_DOMAIN,
                port=switchboard_settings.CHANNEL_MYSQL_PORT,
                encoded=download_request_details.encoded,
            ),
            template=Path(backend_settings.TEMPLATES_PATH) / "mysql_tables.zip",
        ),
        filename=f"{canarydrop.canarytoken.value()}_mysql_dump.sql.gz",
    )


@create_download_response.register
def _(
    download_request_details: DownloadIncidentListCSVRequest, canarydrop: Canarydrop
) -> Response:

    csv_content = canarydrop.get_csv_incident_list()

    return DownloadIncidentListCSVResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=csv_content,
        filename=f"{canarydrop.canarytoken.value()}.csv",
    )


@create_download_response.register
def _(
    download_request_details: DownloadAWSKeysRequest, canarydrop: Canarydrop
) -> Response:
    return DownloadAWSKeysResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=textwrap.dedent(
            f"""
            [default]
            aws_access_key={canarydrop.aws_access_key_id}
            aws_secret_access_key={canarydrop.aws_secret_access_key}
            region={canarydrop.aws_region}
            output={canarydrop.aws_output}
            """
        ).strip(),
        filename="credentials",
        region=canarydrop.aws_region,
        aws_access_key_id=canarydrop.aws_access_key_id,
        aws_secret_access_key=canarydrop.aws_secret_access_key,
        output=canarydrop.aws_output,
    )


@create_download_response.register
def _(
    download_request_details: DownloadKubeconfigRequest, canarydrop: Canarydrop
) -> Response:
    return DownloadKubeconfigResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=b64decode(canarydrop.kubeconfig),
        filename="kubeconfig",
    )


@create_download_response.register
def _(
    download_request_details: DownloadSplackApiRequest, canarydrop: Canarydrop
) -> Response:
    return DownloadSplackApiResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        filename="slack_creds",
    )


@create_download_response.register
def _(
    download_request_details: DownloadQRCodeRequest, canarydrop: Canarydrop
) -> Response:
    return DownloadQRCodeResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=segno.make(canarydrop.token_url).png_data_uri(scale=5),
        filename=f"{canarydrop.canarytoken.value()}.png",
    )


@singledispatch
def create_response(token_request_details, canarydrop: Canarydrop):
    """"""
    raise NotImplementedError("")


@create_response.register
def _(
    token_request_details: DNSTokenRequest, canarydrop: Canarydrop
) -> DNSTokenResponse:
    return DNSTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(
    token_request_details: Log4ShellTokenRequest, canarydrop: Canarydrop
) -> Log4ShellTokenResponse:

    return Log4ShellTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        token_usage=canarydrop.canarytoken.value(),
        url_components=list(canarydrop.get_url_components()),
        # src_data=canarydrop["src_data"],
    )


@create_response.register
def _(
    token_request_details: WindowsDirectoryTokenRequest, canarydrop: Canarydrop
) -> WindowsDirectoryTokenResponse:

    return WindowsDirectoryTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        token_usage=canarydrop.canarytoken.value(),
        url_components=list(canarydrop.get_url_components()),
        # src_data=canarydrop["src_data"],
    )


@create_response.register
def _(
    token_request_details: ClonedWebTokenRequest, canarydrop: Canarydrop
) -> ClonedWebTokenResponse:

    return ClonedWebTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        token_usage=canarydrop.canarytoken.value(),
        url_components=list(canarydrop.get_url_components()),
        clonedsite_js=canarydrop.get_cloned_site_javascript(),
    )


@create_response.register
def _(
    token_request_details: FastRedirectTokenRequest, canarydrop: Canarydrop
) -> FastRedirectTokenResponse:

    return FastRedirectTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        token_usage=canarydrop.canarytoken.value(),
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(
    token_request_details: SlowRedirectTokenRequest, canarydrop: Canarydrop
) -> SlowRedirectTokenResponse:

    return SlowRedirectTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        token_usage=canarydrop.canarytoken.value(),
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(
    token_request_details: WebBugTokenRequest, canarydrop: Canarydrop
) -> WebBugTokenResponse:
    # TODO: add browser_scanner_enabled to WebBugTokenRequest
    # canarydrop.browser_scanner_enabled = True

    return WebBugTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(
    token_request_details: WireguardTokenRequest, canarydrop: Canarydrop
) -> WireguardTokenResponse:
    public_ip = switchboard_settings.PUBLIC_IP
    wg_private_key_seed = switchboard_settings.WG_PRIVATE_KEY_SEED
    wg_private_key_n = switchboard_settings.WG_PRIVATE_KEY_N
    wg_conf = wg.clientConfig(
        canarydrop.wg_key, public_ip, wg_private_key_seed, wg_private_key_n
    )
    qr_code = segno.make(wg_conf).png_data_uri(scale=2)
    return WireguardTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
        # additional information for Wireguard token response
        wg_conf=wg_conf,
        qr_code=qr_code,
    )


@create_response.register
def _(token_request_details: SQLServerTokenRequest, canarydrop: Canarydrop):

    return SQLServerTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _create_aws_key_token_response(
    token_request_details: AWSKeyTokenRequest,
    canarydrop: Canarydrop,
    settings: Optional[Settings] = None,
) -> AWSKeyTokenResponse:

    if settings is None:
        settings = switchboard_settings

    try:
        key = get_aws_key(
            token=canarydrop.canarytoken,
            server=get_all_canary_domains()[0],
            aws_url=settings.AWSID_URL,
            aws_access_key_id=settings.TESTING_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.TESTING_AWS_SECRET_ACCESS_KEY,
        )
    except Exception as e:
        capture_exception(error=e, context=("get_aws_key", None))
        # We can fail by getting 404 from AWSID_URL or failing validation
        return JSONResponse(
            {"message": "Failed to generate AWS Keys. We looking into it."},
            status_code=400,
        )

    canarydrop.aws_access_key_id = key["access_key_id"]
    canarydrop.aws_secret_access_key = key["secret_access_key"]
    canarydrop.aws_region = key["region"]
    canarydrop.aws_output = key["output"]
    canarydrop.token_url = f"{canary_http_channel}/{canarydrop.canarytoken.value()}"
    save_canarydrop(canarydrop)

    return AWSKeyTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
        # additional information for AWS token response
        aws_access_key_id=canarydrop.aws_access_key_id,
        aws_secret_access_key=canarydrop.aws_secret_access_key,
        region=canarydrop.aws_region,
        output=canarydrop.aws_output,
    )


@create_response.register
def _(token_request_details: PDFTokenRequest, canarydrop: Canarydrop):
    return PDFTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.get_url([canary_http_channel]),
        auth_token=canarydrop.auth,
        hostname=canarydrop.get_hostname(nxdomain=True),
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(
    token_request_details: CustomBinaryTokenRequest, canarydrop: Canarydrop
) -> CustomBinaryTokenResponse:
    """Handles the creation storing of a `CustomBinary` token.

    Args:
        token_request_details (CustomBinaryTokenRequest): Request details to make token.
        canarydrop (Canarydrop): Drop to associate with token and store relevant info.

    Raises:
        HTTPException: 400 if file is too large. See MAX_EXE_UPLOAD_SIZE in settings.
        HTTPException: 400 if file is not a .exe or .dll extension.

    Returns:
        CustomBinaryTokenResponse: response with tokened file.
    """

    file_name = token_request_details.signed_exe.filename
    token_request_details.signed_exe.file.seek(0)
    filebody = token_request_details.signed_exe.file.read()

    if not file_name.lower().endswith(("exe", "dll")):
        raise HTTPException(
            status_code=400, detail="Uploaded authenticode file must be an exe or dll"
        )

    if len(filebody) > backend_settings.MAX_EXE_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. File size must be < {size} MB. {size_given} MB given.".format(
                size=backend_settings.MAX_EXE_UPLOAD_SIZE / (1024 * 1024),
                size_given=len(filebody) / (1024 * 1024),
            ),
        )
    signed_contents = make_canary_authenticode_binary(
        nxdomain_token_url=f"http://{canarydrop.get_hostname(nxdomain=True)}",
        filebody=filebody,
    )
    encoded_signed_contents = "data:octet/stream;base64,{base64_file}".format(
        base64_file=base64.b64encode(signed_contents).decode()
    )
    save_canarydrop(canarydrop)
    return CustomBinaryTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.get_hostname(nxdomain=True),
        url_components=list(canarydrop.get_url_components()),
        # additional information for CustomBinary token response
        file_name=file_name,
        file_contents=encoded_signed_contents,
    )


@create_response.register
def _(
    token_request_details: CustomImageTokenRequest, canarydrop: Canarydrop
) -> CustomImageTokenResponse:
    """Creates a response for Custom Image Token. This saves the

    Args:
        token_request_details (CustomImageTokenRequest): Request details.
        canarydrop (Canarydrop): canarydrop that will hold this tokens state.

    Raises:
        HTTPException: status 400 if Image Upload is not supported.
        HTTPException: status 400 if file is not .png, .gif, .jpg
        HTTPException: status 400 if file is too large. See MAX_WEB_IMAGE_UPLOAD_SIZE
        HTTPException: status 400 if failed to save file.

    Returns:
        CustomImageTokenResponse: Custom image response.
    """
    # ensure there is an upload folder
    if not backend_settings.WEB_IMAGE_UPLOAD_PATH:
        raise HTTPException(status_code=400, detail="Image upload not supported")

    # extract uploaded file contents
    filename = token_request_details.web_image.filename

    # check file extension
    if not filename.lower().endswith((".png", ".gif", ".jpg")):
        raise HTTPException(
            status_code=400, detail="Uploaded image must be a PNG, GIF or JPG"
        )

    # extract file bytes and check file size
    token_request_details.web_image.file.seek(0)
    filebody = token_request_details.web_image.file.read()
    if len(filebody) > backend_settings.MAX_WEB_IMAGE_UPLOAD_SIZE:
        max_size = str(backend_settings.MAX_WEB_IMAGE_UPLOAD_SIZE / (1024 * 1024))
        raise HTTPException(
            status_code=400,
            detail=f"File too large. File size must be < {max_size} MB.",
        )
    # create a random local filename
    random_name = hashlib.md5(os.urandom(32)).hexdigest()
    filepath = "{pathjoin}.{extension}".format(
        pathjoin=os.path.join(
            backend_settings.WEB_IMAGE_UPLOAD_PATH, random_name[:2], random_name[2:]
        ),
        extension=filename.lower()[-3:],
    )

    # create local file
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise HTTPException(
                    status_code=400,
                    detail="Something went wrong when creating Custom Image Token ",
                )

    # write to local file
    with open(filepath, "wb") as fp:
        fp.write(filebody)
    # save to canarydrop
    canarydrop.browser_scanner_enabled = False
    canarydrop.web_image_enabled = True
    canarydrop.web_image_path = filepath

    save_canarydrop(canarydrop)
    # add_random_hit_to_drop_for_testing(canarydrop)
    return CustomImageTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(token_request_details: SvnTokenRequest, canarydrop: Canarydrop):

    return SvnTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(token_request_details: MsWordDocumentTokenRequest, canarydrop: Canarydrop):

    return MsWordDocumentTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(token_request_details: MsExcelDocumentTokenRequest, canarydrop: Canarydrop):

    return MsExcelDocumentTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(token_request_details: QRCodeTokenRequest, canarydrop: Canarydrop):
    return QRCodeTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
        # additional information for QRCode token response
        qrcode_png=segno.make(canarydrop.token_url).png_data_uri(scale=5),
    )


@create_response.register
def _(token_request_details: SMTPTokenRequest, canarydrop: Canarydrop):
    return SMTPTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.token_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(token_request_details: KubeconfigTokenRequest, canarydrop: Canarydrop):
    return KubeconfigTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.get_url([canary_http_channel]),
        auth_token=canarydrop.auth,
        hostname=canarydrop.get_hostname(),
        kubeconfig=canarydrop.kubeconfig,
    )


@create_response.register
def _(token_request_details: MySQLTokenRequest, canarydrop: Canarydrop):
    return MySQLTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=HttpUrl(
            canarydrop.get_url(
                [
                    f"{backend_settings.BACKEND_SCHEME}://{switchboard_settings.DOMAINS[0]}"
                ]
            ),
            scheme=backend_settings.BACKEND_SCHEME,
        ),
        auth_token=canarydrop.auth,
        hostname=canarydrop.get_hostname(),
        usage=Canarydrop.generate_mysql_usage(
            canarydrop.canarytoken.value(),
            domain=switchboard_settings.LISTEN_DOMAIN,
            port=switchboard_settings.CHANNEL_MYSQL_PORT,
        ),
    )


@app.get("/commitsha")
def get_commit_sha():
    commit_sha = get_deployed_commit_sha()
    return JSONResponse({"commit_sha": commit_sha}, status_code=200)
