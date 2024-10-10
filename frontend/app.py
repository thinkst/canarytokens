# Design: An API same as before for testing.This could remain separate
# or get pulled into the v3 frontend.
# RFC - V3
# Keeping a frontend separate has a few advantages:
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
from functools import singledispatch
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote

import requests
import segno
import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import APIKeyQuery
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl, ValidationError, parse_obj_as
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration

import canarytokens
import canarytokens.credit_card_v2 as credit_card_infra
from canarytokens import extendtoken, kubeconfig, msreg, queries
from canarytokens import wireguard as wg
from canarytokens.authenticode import make_canary_authenticode_binary
from canarytokens.awskeys import get_aws_key
from canarytokens.azurekeys import get_azure_id
from canarytokens.canarydrop import Canarydrop
from canarytokens.exceptions import CanarydropAuthFailure
from canarytokens.models import (
    PWA_APP_TITLES,
    AnyDownloadRequest,
    AnySettingsRequest,
    AnyTokenRequest,
    AnyTokenResponse,
    AWSKeyTokenRequest,
    AWSKeyTokenResponse,
    AzureIDTokenRequest,
    AzureIDTokenResponse,
    CCTokenRequest,
    CCTokenResponse,
    ClonedWebTokenRequest,
    ClonedWebTokenResponse,
    CSSClonedWebTokenRequest,
    CSSClonedWebTokenResponse,
    DeleteResponse,
    DownloadCSSClonedWebRequest,
    DownloadCSSClonedWebResponse,
    CMDTokenRequest,
    CMDTokenResponse,
    CreditCardV2TokenRequest,
    CreditCardV2TokenResponse,
    CustomBinaryTokenRequest,
    CustomBinaryTokenResponse,
    CustomImageTokenRequest,
    CustomImageTokenResponse,
    DNSTokenRequest,
    DNSTokenResponse,
    DownloadAWSKeysRequest,
    DownloadAWSKeysResponse,
    DownloadAzureIDCertRequest,
    DownloadAzureIDCertResponse,
    DownloadAzureIDConfigRequest,
    DownloadAzureIDConfigResponse,
    DownloadCCRequest,
    DownloadCCResponse,
    DownloadCMDRequest,
    DownloadCMDResponse,
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
    DownloadSlackAPIRequest,
    DownloadSlackAPIResponse,
    DownloadZipRequest,
    DownloadZipResponse,
    FastRedirectTokenRequest,
    FastRedirectTokenResponse,
    HistoryResponse,
    KubeconfigTokenRequest,
    KubeconfigTokenResponse,
    Log4ShellTokenRequest,
    Log4ShellTokenResponse,
    ManageResponse,
    MsExcelDocumentTokenRequest,
    MsExcelDocumentTokenResponse,
    MsWordDocumentTokenRequest,
    MsWordDocumentTokenResponse,
    MySQLTokenRequest,
    MySQLTokenResponse,
    PDFTokenRequest,
    PDFTokenResponse,
    PWATokenRequest,
    PWATokenResponse,
    QRCodeTokenRequest,
    QRCodeTokenResponse,
    response_error,
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
from canarytokens.azure_css import (
    install_azure_css,
    EntraTokenErrorAccessDenied,
    build_entra_redirect_url,
    EntraTokenStatus,
    LEGACY_ENTRA_STATUS_MAP,
)
from canarytokens.pdfgen import make_canary_pdf
from canarytokens.queries import (
    add_canary_domain,
    add_canary_google_api_key,
    add_canary_nxdomain,
    add_canary_page,
    add_canary_path_element,
    get_all_canary_domains,
    get_all_canary_sites,
    is_email_blocked,
    is_valid_email,
    remove_canary_domain,
    save_canarydrop,
    validate_webhook,
    WebhookTooLongError,
)
from canarytokens.redismanager import DB
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.tokens import Canarytoken
from canarytokens.utils import get_deployed_commit_sha
from canarytokens.ziplib import make_canary_zip

frontend_settings = FrontendSettings()
switchboard_settings = SwitchboardSettings()
protocol = "https" if switchboard_settings.FORCE_HTTPS else "http"
if switchboard_settings.USING_NGINX:
    canary_http_channel = f"{protocol}://{frontend_settings.DOMAINS[0]}"
else:
    canary_http_channel = f"{protocol}://{frontend_settings.DOMAINS[0]}:{switchboard_settings.CHANNEL_HTTP_PORT}"

if frontend_settings.SENTRY_DSN and frontend_settings.SENTRY_ENABLE:
    sentry_sdk.init(
        dsn=frontend_settings.SENTRY_DSN,
        environment=frontend_settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=0.2,
        integrations=[
            RedisIntegration(),
            FastApiIntegration(),
        ],
        release=get_deployed_commit_sha(),
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
    title=frontend_settings.API_APP_TITLE,
    version=canarytokens.__version__,
)

vue_index = Jinja2Templates(directory="../dist/")


if frontend_settings.NEW_UI:

    @app.get("/")
    @app.get("/nest/legal")
    @app.get("/manage")
    @app.get("/nest/manage/{rest_of_path:path}")
    @app.get("/history")
    @app.get("/nest/history/{rest_of_path:path}")
    @app.get("/nest/entra/{rest_of_path:path}")
    @app.get("/nest/generate")
    @app.get("/generate")
    def index(request: Request):
        return vue_index.TemplateResponse("index.html", {"request": request})


ROOT_API_ENDPOINT = "/d3aece8093b71007b5ccfedad91ebb11"

api = FastAPI(
    title=frontend_settings.API_APP_TITLE,
    version=canarytokens.__version__,
    openapi_prefix=ROOT_API_ENDPOINT,
    openapi_tags=tags_metadata,
    docs_url=None,  # should be None on prod
    redoc_url=frontend_settings.API_REDOC_URL,  # should default to None on prod
)

app.mount(ROOT_API_ENDPOINT, api)
app.mount(
    frontend_settings.STATIC_FILES_APPLICATION_SUB_PATH,
    StaticFiles(directory=frontend_settings.STATIC_FILES_PATH),
    name=frontend_settings.STATIC_FILES_APPLICATION_INTERNAL_NAME,
)

if frontend_settings.NEW_UI:
    try:
        app.mount(
            "/nest",
            StaticFiles(directory="../dist/", html=True),
            name="Vue Frontend Dist",
        )
    except RuntimeError:
        print("Error: No Vue dist found. Is this the test Action?")

templates = Jinja2Templates(directory=frontend_settings.TEMPLATES_PATH)

if (
    frontend_settings.SENTRY_DSN
    and frontend_settings.SENTRY_ENABLE
    and switchboard_settings.PUBLIC_DOMAIN != "127.0.0.1"
):
    # Add sentry when running on a domain.
    app.add_middleware(SentryAsgiMiddleware)
    print(f"Sentry enabled. Environment: {frontend_settings.SENTRY_ENVIRONMENT}")


def capture_exception(error: BaseException, context: tuple[str, Any]):
    if frontend_settings.SENTRY_DSN and frontend_settings.SENTRY_ENABLE:
        with sentry_sdk.configure_scope() as scope:
            scope.set_context(*context)
            sentry_sdk.capture_exception(error)


auth_key = APIKeyQuery(name="auth", description="Auth key for a token")


async def _parse_for_x(request: Request, expected_type: Any) -> Any:
    data: Any
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
    get_canarydrop_and_authenticate(token=data["token"], auth=data["auth"])


def get_canarydrop_and_authenticate(token: str, auth: str = Security(auth_key)):
    try:
        canarydrop = queries.get_canarydrop_and_authenticate(token=token, auth=auth)
    except CanarydropAuthFailure:
        raise HTTPException(
            status_code=403, detail="Token not found. Invalid `auth` and `token` pair."
        )
    return canarydrop


@app.on_event("startup")
def startup_event():
    DB.set_db_details(
        hostname=switchboard_settings.REDIS_HOST, port=switchboard_settings.REDIS_PORT
    )
    remove_canary_domain()
    remove_canary_domain()

    add_canary_domain(domain=frontend_settings.DOMAINS[0])
    if frontend_settings.GOOGLE_API_KEY:
        add_canary_google_api_key(frontend_settings.GOOGLE_API_KEY)
    add_canary_nxdomain(domain=frontend_settings.NXDOMAINS[0])
    add_canary_path_element(path_element="stuff")
    add_canary_page("payments.js")


# When the New UI is stable we can remove this entire "app" block up until the next comment


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
        "awsid_enabled": frontend_settings.AWSID_URL is not None,
        "azureid_enabled": frontend_settings.AZURE_ID_TOKEN_URL is not None,
    }
    return templates.TemplateResponse("generate_new.html", generate_template_params)


@app.post(
    "/generate",
    tags=["Create Canarytokens"],
)
async def generate(request: Request) -> AnyTokenResponse:  # noqa: C901  # gen is large
    """
    Generate a token and return the appropriate TokenResponse
    """

    if request.headers.get("Content-Type", "application/json") == "application/json":
        token_request_data = await request.json()
    else:
        # Need a mutable copy of the form data
        token_request_data = dict(await request.form())
        token_request_data["token_type"] = token_request_data.pop(
            "type", token_request_data.get("token_type", None)
        )

    try:
        token_request_details: AnyTokenRequest = parse_obj_as(
            AnyTokenRequest, token_request_data
        )
    except ValidationError:  # DESIGN: can we specialise on what went wrong?
        return response_error(1, "Malformed request, invalid data supplied.")

    if not token_request_details.memo:
        return response_error(2, "No memo supplied")

    if token_request_details.webhook_url:
        try:
            validate_webhook(
                token_request_details.webhook_url, token_request_details.token_type
            )
        except WebhookTooLongError:
            return response_error(3, "Webhook URL too long. Use a shorter webhook URL.")
        except requests.exceptions.HTTPError:
            return response_error(
                3, "Invalid webhook supplied. Confirm you can POST to this URL."
            )
        except requests.exceptions.Timeout:
            return response_error(
                3, "Webhook timed out. Confirm you can POST to this URL."
            )
        except requests.exceptions.ConnectionError:
            return response_error(
                3, "Failed to connect to webhook. Confirm you can POST to this URL."
            )

    if token_request_details.email:
        if not is_valid_email(token_request_details.email):
            return response_error(5, "Invalid email supplied")

        if is_email_blocked(token_request_details.email):
            # raise HTTPException(status_code=400, detail="Email is blocked.")
            return response_error(
                6,
                "Blocked email supplied. Please see our Acceptable Use Policy at https://canarytokens.org/legal",
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
        alert_email_enabled=True if token_request_details.email else False,
        alert_email_recipient=token_request_details.email,
        alert_webhook_enabled=True if token_request_details.webhook_url else False,
        alert_webhook_url=token_request_details.webhook_url or "",
        canarytoken=canarytoken,
        memo=token_request_details.memo,
        browser_scanner_enabled=False,
        # Drop details to fulfil the tokens promise.
        # TODO: move all token type specific canary drop
        #       attribute setting into `create_response`
        #       which is already doing the type dispatch for us.
        kubeconfig=kube_config,
        redirect_url=getattr(token_request_details, "redirect_url", None),
        clonedsite=getattr(token_request_details, "clonedsite", None),
        expected_referrer=getattr(token_request_details, "expected_referrer", None),
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
    canarydrop.get_url(canary_domains=[canary_http_channel])
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
    request: Request, canarydrop: Canarydrop = Depends(get_canarydrop_and_authenticate)
) -> HTMLResponse:

    manage_template_params = {
        "request": request,
        "canarydrop": canarydrop,
        "API_KEY": queries.get_canary_google_api_key(),
        "now": datetime.datetime.now(),
        "public_ip": frontend_settings.PUBLIC_IP,
        "wg_private_key_seed": switchboard_settings.WG_PRIVATE_KEY_SEED,
        "wg_private_key_n": switchboard_settings.WG_PRIVATE_KEY_N,
    }

    if canarydrop.type == TokenTypes.WIREGUARD:
        wg_conf = wg.clientConfig(
            canarydrop.wg_key,
            frontend_settings.PUBLIC_IP,
            switchboard_settings.WG_PRIVATE_KEY_SEED,
            switchboard_settings.WG_PRIVATE_KEY_N,
        )
        qr_code = segno.make(wg_conf).png_data_uri(scale=2)
        manage_template_params["wg_conf"] = wg_conf
        manage_template_params["wg_qr_code"] = qr_code
    elif canarydrop.type == TokenTypes.QR_CODE:
        qr_code = segno.make(canarydrop.generated_url).png_data_uri(scale=5)
        manage_template_params["qr_code"] = qr_code
    elif canarydrop.type == TokenTypes.CLONEDSITE:
        manage_template_params["force_https"] = switchboard_settings.FORCE_HTTPS

    return templates.TemplateResponse("manage_new.html", manage_template_params)


@app.get(
    "/history",
    tags=["Canarytokens History"],
    response_class=HTMLResponse,
    dependencies=[Depends(authorise_token_access)],
)
async def history_page_get(
    request: Request, canarydrop: Canarydrop = Depends(get_canarydrop_and_authenticate)
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
    canarydrop = queries.get_canarydrop_and_authenticate(
        token=settings_request.token, auth=settings_request.auth
    )
    if canarydrop.apply_settings_change(setting_request=settings_request):
        return JSONResponse({"message": "success"})
    else:
        return JSONResponse({"message": "failure"}, status_code=400)


@app.get(
    "/legal",
    tags=["Canarytokens legal page"],
    response_class=HTMLResponse,
)
def legal_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("legal.html", {"request": request})


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
    canarydrop = queries.get_canarydrop_and_authenticate(
        token=download_request.token, auth=download_request.auth
    )
    return create_download_response(download_request, canarydrop=canarydrop)


@app.get("/commitsha")
def get_commit_sha():
    commit_sha = get_deployed_commit_sha()
    return JSONResponse({"commit_sha": commit_sha}, status_code=200)


# remove up until here once new ui stable


# NOTE: Do not remove this when cleaning up after UI is stable
@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("500.html", {"request": request})


@app.exception_handler(404)
async def internal_not_found_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("404.html", {"request": request})


# NOTE: Do not remove this when cleaning up after UI is stable
@app.get("/azure_css_landing", tags=["Azure Portal Phishing Protection App"])
async def azure_css_landing(
    request: Request,
    admin_consent: Optional[str] = None,
    tenant: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
) -> HTMLResponse:
    """
    This page is loaded after a user has authN and authZ'd into their tenant and granted the permissions to install the CSS
    Once the CSS is installed into their tenant, and we revoke our permission grants, we can close the window as this will happen in
    a pop-up context.
    """
    css = b64decode(unquote(state)).decode()

    if not admin_consent == "True" or error == EntraTokenErrorAccessDenied:
        status = EntraTokenStatus.ENTRA_STATUS_NO_ADMIN_CONSENT
    else:
        status = install_azure_css(tenant, css)

    if not frontend_settings.NEW_UI:
        return templates.TemplateResponse(
            "azure_install.html",
            {"request": request, "status": LEGACY_ENTRA_STATUS_MAP[status.value]},
        )

    return RedirectResponse(build_entra_redirect_url(status.value))


def _manually_build_docs_schema(model) -> dict:
    """
    Some endpoints determine how to unpack their requests inside the function and so we don't know the request types to include in the docs.
    This manually builds the model schemas so we can see this stuff in the /api/redoc page.
    """

    return {
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "anyOf": [
                            schema.schema()
                            for schema in list(model.__args__[0].__args__)
                        ],
                    },
                }
            },
            "required": True,
        },
    }


@api.post(
    "/generate",
    tags=["Create Canarytokens"],
    response_model=AnyTokenResponse,
    openapi_extra=_manually_build_docs_schema(AnyTokenRequest),
)
async def api_generate(  # noqa: C901  # gen is large
    request: Request,
) -> AnyTokenResponse:
    """
    Generate a token and return the appropriate TokenResponse
    """

    if request.headers.get("Content-Type", "application/json") == "application/json":
        token_request_data = await request.json()
    else:
        # Need a mutable copy of the form data
        token_request_data = dict(await request.form())
        token_request_data["token_type"] = token_request_data.pop(
            "type", token_request_data.get("token_type", None)
        )

    try:
        token_request_details = parse_obj_as(AnyTokenRequest, token_request_data)
    except ValidationError:  # DESIGN: can we specialise on what went wrong?
        return response_error(1, "Malformed request, invalid data supplied.")

    if not token_request_details.memo:
        return response_error(2, "No memo supplied")

    if token_request_details.webhook_url:
        try:
            validate_webhook(
                token_request_details.webhook_url, token_request_details.token_type
            )
        except WebhookTooLongError:
            return response_error(3, "Webhook URL too long. Use a shorter webhook URL.")
        except requests.exceptions.HTTPError:
            return response_error(
                3, "Invalid webhook supplied. Confirm you can POST to this URL."
            )
        except requests.exceptions.Timeout:
            return response_error(
                3, "Webhook timed out. Confirm you can POST to this URL."
            )
        except requests.exceptions.ConnectionError:
            return response_error(
                3, "Failed to connect to webhook. Confirm you can POST to this URL."
            )

    if token_request_details.email:
        if not is_valid_email(token_request_details.email):
            return response_error(5, "Invalid email supplied")

        if is_email_blocked(token_request_details.email):
            # raise HTTPException(status_code=400, detail="Email is blocked.")
            return response_error(
                6,
                "Blocked email supplied. Please see our Acceptable Use Policy at https://canarytokens.org/legal",
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
        alert_email_enabled=True if token_request_details.email else False,
        alert_email_recipient=token_request_details.email,
        alert_webhook_enabled=True if token_request_details.webhook_url else False,
        alert_webhook_url=token_request_details.webhook_url or "",
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
        expected_referrer=getattr(token_request_details, "expected_referrer", None),
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
    canarydrop.get_url(
        canary_domains=[canary_http_channel],
        page="index.html"
        if token_request_details.token_type == TokenTypes.PWA
        else None,
    )
    if token_request_details.token_type == TokenTypes.PWA:
        canarydrop.generated_url = canarydrop.generated_url.replace(
            "http://", "https://"
        )
    canarydrop.generated_hostname = canarydrop.get_hostname()

    if token_request_details.token_type != TokenTypes.CREDIT_CARD_V2:
        save_canarydrop(canarydrop)

    return create_response(token_request_details, canarydrop)


@api.get(
    "/manage",
    tags=["Manage Canarytokens"],
    response_model=ManageResponse,
)
async def api_manage_canarytoken(token: str, auth: str) -> ManageResponse:
    canarydrop = get_canarydrop_and_authenticate(token=token, auth=auth)

    response = {"canarydrop": canarydrop}

    if canarydrop.type == TokenTypes.WIREGUARD:
        wg_conf = wg.clientConfig(
            canarydrop.wg_key,
            frontend_settings.PUBLIC_IP,
            switchboard_settings.WG_PRIVATE_KEY_SEED,
            switchboard_settings.WG_PRIVATE_KEY_N,
        )
        qr_code = segno.make(wg_conf).png_data_uri(scale=2)
        response["wg_conf"] = wg_conf
        response["wg_qr_code"] = qr_code
    elif canarydrop.type == TokenTypes.QR_CODE:
        qr_code = segno.make(canarydrop.generated_url).png_data_uri(scale=5)
        response["qr_code"] = qr_code
    elif canarydrop.type == TokenTypes.CLONEDSITE:
        response["force_https"] = switchboard_settings.FORCE_HTTPS
        response["clonedsite_js"] = canarydrop.get_cloned_site_javascript(
            switchboard_settings.FORCE_HTTPS
        )
    elif canarydrop.type == TokenTypes.CSSCLONEDSITE:
        response["clonedsite_css"] = canarydrop.get_cloned_site_css(
            frontend_settings.CLOUDFRONT_URL
        )
        response["client_id"] = frontend_settings.AZUREAPP_ID

    return ManageResponse(**response)


@api.get(
    "/history",
    tags=["Canarytokens History"],
    response_model=HistoryResponse,
)
async def api_history(token: str, auth: str) -> HistoryResponse:
    canarydrop = get_canarydrop_and_authenticate(token=token, auth=auth)
    response = {
        "canarydrop": canarydrop,
        "history": canarydrop.triggered_details,
        "google_api_key": queries.get_canary_google_api_key(),
    }
    return HistoryResponse(**response)


@api.post("/delete", response_model=DeleteResponse)
async def api_delete(request: Request) -> DeleteResponse:
    data = await request.json()
    token = data.get("token", "")
    auth = data.get("auth", "")
    canarydrop = get_canarydrop_and_authenticate(token=token, auth=auth)
    queries.delete_canarydrop(canarydrop)
    return DeleteResponse(message="success")


@api.post(
    "/settings",
    tags=["Canarytokens Settings"],
    response_model=SettingsResponse,
)
async def api_settings_post(
    response: Response,
    settings_request: AnySettingsRequest,
) -> SettingsResponse:
    canarydrop = get_canarydrop_and_authenticate(
        token=settings_request.token, auth=settings_request.auth
    )
    if canarydrop.apply_settings_change(setting_request=settings_request):
        return SettingsResponse(**{"message": "success"})
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return SettingsResponse(**{"message": "failure"})


@api.get(
    "/download",
    tags=["Canarytokens Downloads"],
    openapi_extra=_manually_build_docs_schema(AnyDownloadRequest),
)
async def api_download(
    download_request: AnyDownloadRequest = Depends(parse_for_download),
) -> Response:
    """
    Given `AnyDownloadRequest` a canarydrop is retrieved and the token
    artifact or hit information is returned.
    """
    canarydrop = get_canarydrop_and_authenticate(
        token=download_request.token, auth=download_request.auth
    )
    return create_download_response(download_request, canarydrop=canarydrop)


@api.get("/commitsha")
def api_get_commit_sha():
    commit_sha = get_deployed_commit_sha()
    return JSONResponse({"commit_sha": commit_sha}, status_code=200)


@singledispatch
def create_download_response(download_request_details, canarydrop: Canarydrop):
    """"""
    raise NotImplementedError(
        f"DownloadRequest {download_request_details} not supported."
    )


@create_download_response.register
def _(
    download_request_details: DownloadCMDRequest, canarydrop: Canarydrop
) -> DownloadCMDResponse:
    """"""
    return DownloadCMDResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=msreg.make_canary_msreg(
            token_hostname=canarydrop.get_hostname(),
            process_name=canarydrop.cmd_process,
        ),
        filename=f"{canarydrop.canarytoken.value()}.reg",
    )


@create_download_response.register
def _(
    download_request_details: DownloadCCRequest, canarydrop: Canarydrop
) -> DownloadCCResponse:
    """"""
    return DownloadCCResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=canarydrop.cc_rendered_csv,
        filename=f"{canarydrop.canarytoken.value()}.csv",
    )


@create_download_response.register
def _(
    download_request_details: DownloadCSSClonedWebRequest, canarydrop: Canarydrop
) -> DownloadCSSClonedWebResponse:
    """"""
    return DownloadCSSClonedWebResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=canarydrop.get_cloned_site_css(frontend_settings.CLOUDFRONT_URL),
        filename=f"{canarydrop.canarytoken.value()}.css",
    )


@create_download_response.register
def _(
    download_request_details: DownloadMSWordRequest, canarydrop: Canarydrop
) -> Response:

    return DownloadMSWordResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=make_canary_msword(
            canarydrop.generated_url,
            template=Path(frontend_settings.TEMPLATES_PATH) / "template.docx",
        ),
        filename=f"{canarydrop.canarytoken.value()}.docx",
    )


@create_download_response.register
def _(download_request_details: DownloadZipRequest, canarydrop: Canarydrop) -> Response:
    hostname = f"{canarydrop.canarytoken.value()}.{frontend_settings.DOMAINS[0]}"
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
            canarydrop.generated_url,
            template=Path(frontend_settings.TEMPLATES_PATH) / "template.xlsx",
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
            template=Path(frontend_settings.TEMPLATES_PATH) / "template.pdf",
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
                domain=frontend_settings.DOMAINS[0],
                port=switchboard_settings.CHANNEL_MYSQL_PORT,
                encoded=download_request_details.encoded,
            ),
            template=Path(frontend_settings.TEMPLATES_PATH) / "mysql_tables.zip",
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
    download_request_details: DownloadAzureIDConfigRequest, canarydrop: Canarydrop
) -> Response:
    return DownloadAzureIDConfigResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=textwrap.dedent(
            f"""
            {{
              "appId": "{canarydrop.app_id}",
              "displayName": "azure-cli-{canarydrop.cert_name}",
              "fileWithCertAndPrivateKey": "{canarydrop.cert_file_name}",
              "password": null,
              "tenant": "{canarydrop.tenant_id}"
            }}
            """
        ).strip(),
        filename=canarydrop.cert_file_name.replace(".pem", ".json")
        if canarydrop.cert_file_name.endswith(".pem")
        else canarydrop.cert_file_name,
    )


@create_download_response.register
def _(
    download_request_details: DownloadAzureIDCertRequest, canarydrop: Canarydrop
) -> Response:
    return DownloadAzureIDCertResponse(
        token=download_request_details.token,
        auth=download_request_details.auth,
        content=canarydrop.cert,
        filename=canarydrop.cert_file_name,
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
    download_request_details: DownloadSlackAPIRequest, canarydrop: Canarydrop
) -> Response:
    return DownloadSlackAPIResponse(
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
        content=segno.make(canarydrop.generated_url).png_data_uri(scale=5),
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
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        token_usage=canarydrop.canarytoken.value(),
        url_components=list(canarydrop.get_url_components()),
        clonedsite_js=canarydrop.get_cloned_site_javascript(
            switchboard_settings.FORCE_HTTPS
        ),
    )


@create_response.register
def _(
    token_request_details: CSSClonedWebTokenRequest, canarydrop: Canarydrop
) -> CSSClonedWebTokenResponse:

    return CSSClonedWebTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.generated_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        token_usage=canarydrop.canarytoken.value(),
        url_components=list(canarydrop.get_url_components()),
        css=canarydrop.get_cloned_site_css(frontend_settings.CLOUDFRONT_URL),
        client_id=frontend_settings.AZUREAPP_ID,
    )


@create_response.register
def _(
    token_request_details: FastRedirectTokenRequest, canarydrop: Canarydrop
) -> FastRedirectTokenResponse:

    return FastRedirectTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
    )


@create_response.register
def _(
    token_request_details: PWATokenRequest, canarydrop: Canarydrop
) -> PWATokenResponse:
    canarydrop.pwa_icon = token_request_details.icon
    if token_request_details.app_name:
        canarydrop.pwa_app_name = token_request_details.app_name
    else:
        canarydrop.pwa_app_name = PWA_APP_TITLES[token_request_details.icon]
    save_canarydrop(canarydrop)

    return PWATokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.generated_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
        pwa_icon=canarydrop.pwa_icon.value,
        pwa_app_name=canarydrop.pwa_app_name,
    )


@create_response.register
def _(
    token_request_details: WireguardTokenRequest, canarydrop: Canarydrop
) -> WireguardTokenResponse:
    public_ip = frontend_settings.PUBLIC_IP
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
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
        sql_server_sql_action=canarydrop.sql_server_sql_action,
        sql_server_table_name=canarydrop.sql_server_table_name,
        sql_server_view_name=canarydrop.sql_server_view_name,
        sql_server_function_name=canarydrop.sql_server_function_name,
        sql_server_trigger_name=canarydrop.sql_server_trigger_name,
    )


@create_response.register
def _create_aws_key_token_response(
    token_request_details: AWSKeyTokenRequest,
    canarydrop: Canarydrop,
    settings: Optional[FrontendSettings] = None,
) -> AWSKeyTokenResponse:

    if settings is None:
        settings = frontend_settings

    if settings.AWSID_URL is None:
        return JSONResponse(
            {
                "message": "This Canarytokens instance does not have AWS ID tokens enabled."
            },
            status_code=500,
        )

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
    if aws_account_id := key.get("aws_account_id", False):
        canarydrop.aws_account_id = aws_account_id
    canarydrop.generated_url = f"{canary_http_channel}/{canarydrop.canarytoken.value()}"
    save_canarydrop(canarydrop)

    return AWSKeyTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.generated_url,
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
def _create_azure_id_token_response(
    token_request_details: AzureIDTokenRequest,
    canarydrop: Canarydrop,
    settings: Optional[FrontendSettings] = None,
) -> AzureIDTokenResponse:
    if settings is None:
        settings = frontend_settings

    if settings.AZURE_ID_TOKEN_URL is None:
        return JSONResponse(
            {
                "message": "This Canarytokens instance does not have Azure ID tokens enabled."
            },
            status_code=400,
        )

    try:
        key = get_azure_id(
            token=canarydrop.canarytoken,
            server=get_all_canary_domains()[0],
            cert_file_name=token_request_details.azure_id_cert_file_name,
            azure_url=HttpUrl(
                f"{settings.AZURE_ID_TOKEN_URL}?code={settings.AZURE_ID_TOKEN_AUTH}",
                scheme=settings.AZURE_ID_TOKEN_URL.scheme,
            ),
        )
    except Exception as e:
        capture_exception(error=e, context=("get_azure_id", None))
        # We can fail by getting 404 from AZURE_ID_URL or failing validation
        return response_error(
            4, message="Failed to generate Azure IDs. We looking into it."
        )

    canarydrop.cert_file_name = key["cert_file_name"]
    canarydrop.app_id = key["app_id"]
    canarydrop.cert = key["cert"]
    canarydrop.tenant_id = key["tenant_id"]
    canarydrop.cert_name = key["cert_name"]
    canarydrop.generated_url = f"{canary_http_channel}/{canarydrop.canarytoken.value()}"
    save_canarydrop(canarydrop)
    return AzureIDTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.generated_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
        # additional information for Azure token response
        cert_file_name=canarydrop.cert_file_name,
        app_id=canarydrop.app_id,
        cert=canarydrop.cert,
        tenant_id=canarydrop.tenant_id,
        cert_name=canarydrop.cert_name,
    )


@create_response.register
def _(
    token_request_details: CMDTokenRequest, canarydrop: Canarydrop
) -> CMDTokenResponse:
    canarydrop.cmd_process = token_request_details.cmd_process
    queries.save_canarydrop(canarydrop=canarydrop)
    return CMDTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.get_url([canary_http_channel]),
        auth_token=canarydrop.auth,
        hostname=canarydrop.get_hostname(),
        url_components=list(canarydrop.get_url_components()),
        reg_file=msreg.make_canary_msreg(
            token_hostname=canarydrop.get_hostname(),
            process_name=canarydrop.cmd_process,
        ),
    )


@create_response.register
def _(token_request_details: CCTokenRequest, canarydrop: Canarydrop) -> CCTokenResponse:
    eapi = extendtoken.ExtendAPI(
        email=frontend_settings.EXTEND_EMAIL,
        password=frontend_settings.EXTEND_PASSWORD.get_secret_value(),
        card_name=frontend_settings.EXTEND_CARD_NAME,
    )
    try:
        cc = eapi.create_credit_card(token_url=canarydrop.generated_url)
    except extendtoken.ExtendAPIRateLimitException:
        return response_error(
            4, "Credit Card Rate-Limiting currently in place. Please try again later."
        )

    if not cc or not cc.number:
        return response_error(
            4, "Failed to generate credit card. Please contact support@thinkst.com."
        )
    canarydrop.cc_kind = cc.kind
    canarydrop.cc_number = cc.number
    canarydrop.cc_cvc = cc.cvc
    canarydrop.cc_expiration = cc.expiration
    canarydrop.cc_name = cc.name
    canarydrop.cc_billing_zip = cc.billing_zip
    canarydrop.cc_rendered_html = cc.render_html()
    canarydrop.cc_rendered_csv = cc.to_csv()
    queries.save_canarydrop(canarydrop=canarydrop)

    return CCTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url
        if canarydrop.alert_webhook_url
        else "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.get_url([canary_http_channel]),
        auth_token=canarydrop.auth,
        hostname=canarydrop.get_hostname(),
        url_components=list(canarydrop.get_url_components()),
        kind=canarydrop.cc_kind,
        number=canarydrop.cc_number,
        cvc=canarydrop.cc_cvc,
        expiration=canarydrop.cc_expiration,
        name=canarydrop.cc_name,
        billing_zip=canarydrop.cc_billing_zip,
        rendered_html=canarydrop.cc_rendered_html,
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
        HTTPException: 400 if file is too large. See MAX_UPLOAD_SIZE in settings.
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

    if len(filebody) > frontend_settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. File size must be < {size} MB. {size_given} MB given.".format(
                size=frontend_settings.MAX_UPLOAD_SIZE / (1024 * 1024),
                size_given=len(filebody) / (1024 * 1024),
            ),
        )
    signed_contents = make_canary_authenticode_binary(
        nxdomain_token_url=canarydrop.get_hostname(nxdomain=True, as_url=True),
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
        token_url=canarydrop.generated_url,
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
        HTTPException: status 400 if file is too large. See MAX_UPLOAD_SIZE
        HTTPException: status 400 if failed to save file.

    Returns:
        CustomImageTokenResponse: Custom image response.
    """
    # ensure there is an upload folder
    if not frontend_settings.WEB_IMAGE_UPLOAD_PATH:
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
    if len(filebody) > frontend_settings.MAX_UPLOAD_SIZE:
        max_size = str(frontend_settings.MAX_UPLOAD_SIZE / (1024 * 1024))
        raise HTTPException(
            status_code=400,
            detail=f"File too large. File size must be < {max_size} MB.",
        )
    # create a random local filename
    random_name = hashlib.md5(os.urandom(32)).hexdigest()
    filepath = "{pathjoin}.{extension}".format(
        pathjoin=os.path.join(
            frontend_settings.WEB_IMAGE_UPLOAD_PATH, random_name[:2], random_name[2:]
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
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
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
        token_url=canarydrop.generated_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
        # additional information for QRCode token response
        qrcode_png=segno.make(canarydrop.generated_url).png_data_uri(scale=5),
    )


@create_response.register
def _(token_request_details: SMTPTokenRequest, canarydrop: Canarydrop):
    return SMTPTokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.generated_url,
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
                    f"{switchboard_settings.SWITCHBOARD_SCHEME}://{frontend_settings.DOMAINS[0]}"
                ]
            ),
            scheme=switchboard_settings.SWITCHBOARD_SCHEME,
        ),
        auth_token=canarydrop.auth,
        hostname=canarydrop.get_hostname(),
        usage=Canarydrop.generate_mysql_usage(
            canarydrop.canarytoken.value(),
            domain=frontend_settings.DOMAINS[0],
            port=switchboard_settings.CHANNEL_MYSQL_PORT,
        ),
    )


@create_response.register
def _(
    token_request_details: CreditCardV2TokenRequest, canarydrop: Canarydrop
) -> CreditCardV2TokenResponse:
    canarytoken = Canarytoken()
    canarydrop.canarytoken = canarytoken

    (status, card) = credit_card_infra.create_card(canarytoken.value())

    if status == credit_card_infra.Status.SUCCESS:
        canarydrop.cc_v2_card_id = card.card_id
        canarydrop.cc_v2_card_number = card.card_number
        canarydrop.cc_v2_cvv = card.cvv
        canarydrop.cc_v2_expiry_month = card.expiry_month
        canarydrop.cc_v2_expiry_year = card.expiry_year
    elif status == credit_card_infra.Status.NO_MORE_CREDITS:
        return JSONResponse(
            {"message": "No more Card Credits available."}, status_code=500
        )
    else:
        return JSONResponse({"message": "Something went wrong!"}, status_code=500)

    save_canarydrop(canarydrop)

    return CreditCardV2TokenResponse(
        email=canarydrop.alert_email_recipient or "",
        webhook_url=canarydrop.alert_webhook_url or "",
        token=canarydrop.canarytoken.value(),
        token_url=canarydrop.generated_url,
        auth_token=canarydrop.auth,
        hostname=canarydrop.generated_hostname,
        url_components=list(canarydrop.get_url_components()),
        name_on_card=canarydrop.cc_v2_name_on_card,
        card_number=canarydrop.cc_v2_card_number,
        cvv=canarydrop.cc_v2_cvv,
        expiry_month=canarydrop.cc_v2_expiry_month,
        expiry_year=canarydrop.cc_v2_expiry_year,
    )
