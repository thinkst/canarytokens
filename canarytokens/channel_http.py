from typing import Optional

from pydantic import ValidationError, parse_obj_as
from twisted.application import internet
from twisted.logger import Logger
from twisted.python.failure import Failure

# from canarytokens.channel_dns import create_token_hit
from twisted.web import resource, server
from twisted.web.resource import EncodingResourceWrapper, Resource
from twisted.web.server import GzipEncoderFactory, Request

from canarytokens import queries
from canarytokens.channel import InputChannel
from canarytokens.constants import INPUT_CHANNEL_HTTP
from canarytokens.exceptions import NoCanarytokenFound, NoCanarydropFound
from canarytokens.models import AnyTokenHit, TokenTypes
from canarytokens.queries import get_canarydrop
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken, GIF
from canarytokens.utils import coerce_to_float

log = Logger()

# from jinja2 import Environment, FileSystemLoader


# from canarytokens.settings import


class CanarytokenPage(InputChannel, resource.Resource):
    CHANNEL = INPUT_CHANNEL_HTTP
    isLeaf = True
    GIF = (
        "\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
        + "\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00"
        + "\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
    )  # 1x1 GIF

    def __init__(
        self,
        switchboard: Switchboard,
        switchboard_scheme: str,
        switchboard_hostname: str,
        name: Optional[str] = None,
        unique_channel: bool = False,
    ) -> None:
        name = name or self.CHANNEL
        super().__init__(
            switchboard,
            switchboard_scheme,
            switchboard_hostname,
            name,
            unique_channel,
        )

    def getChild(self, name, request):
        if name == "":
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request: Request):
        # A GET request to a token URL can trigger one of a few responses:
        # 1. Check if link has been clicked on (rather than loaded from an
        #    <img>) by looking at the Accept header, then:
        #  1a. If browser security if enabled, serve that page and stop.
        #  1b. If fortune in enabled, serve a fortune and stop.
        # 2. Otherwise we'll serve an image:
        #  2a. If a custom image is attached to the canarydrop, serve that and stop.
        #  2b. Serve our default 1x1 gif

        try:
            manage_uris = [
                b"/generate",
                b"/download?",
                b"/history?",
                b"/manage?",
                b"/resources/",
                b"/settings",
            ]
            if any([request.path.find(x) >= 0 for x in manage_uris]):
                canarytoken = Canarytoken(value=request.path)
            else:
                canarytoken = Canarytoken(value=request.uri)
        except NoCanarytokenFound as e:
            log.info(
                f"HTTP {request.method} on path {request.path} did not correspond to a token. Error: {e}"
            )
            request.setHeader("Content-Type", "image/gif")
            return GIF

        try:
            canarydrop = get_canarydrop(canarytoken)
        except NoCanarydropFound as e:
            log.info(f"Error: {e}")
            request.setHeader("Content-Type", "image/gif")
            return GIF

        handler = getattr(Canarytoken, f"_get_info_for_{canarydrop.type}")
        http_general_info, src_data = handler(request)

        # TODO we should fail gracefully when third party dependency fails
        geo_info = queries.get_geoinfo(ip=http_general_info["src_ip"])

        hit_info = {
            "token_type": canarydrop.type,
            "input_channel": self.CHANNEL,
            **src_data,
            **http_general_info,
            "geo_info": geo_info,
        }
        try:
            token_hit = parse_obj_as(
                AnyTokenHit,
                hit_info,
            )
        except ValidationError as e:
            log.critical(
                f"Failed to parse HTTP token hit. Token: {canarydrop.canarytoken.value()} Hit Info: {hit_info} Error: {e}",
                log_failure=Failure(e),
            )
            return
        canarydrop.add_canarydrop_hit(token_hit=token_hit)
        self.dispatch(canarydrop=canarydrop, token_hit=token_hit)
        # TODO: fix this. Making it type dispatched?
        resp = getattr(Canarytoken, f"_get_response_for_{canarydrop.type}")(
            canarydrop, request
        )
        request.setHeader("Server", "Apache")
        return resp

    def render_OPTIONS(self, request: Request):
        """
        Alert as if it is a normal GET request, but return the expected content and headers.
        """
        _ = self.render_GET(request)
        request.setHeader("Allow", "OPTIONS, GET, POST")
        request.setResponseCode(200)
        request.responseHeaders.removeHeader("Content-Type")
        return b""

    def render_POST(self, request: Request):
        try:
            token = Canarytoken(value=request.path)
        except NoCanarytokenFound:
            log.info(f"No token found in {request.path=}.")
            return b"failed"

        try:
            canarydrop = get_canarydrop(token)
        except NoCanarydropFound as e:
            log.info(f"Canarydrop not found for token {token.value()}. Error: {e}")
            return b"failed"
        # if key and token args are present, we are either:
        #    -posting browser info
        #    -getting an aws trigger (key == aws_s3)
        # otherwise, slack api token data perhaps
        # store the info and don't re-render

        if canarydrop.type == TokenTypes.AWS_KEYS:
            token_hit = Canarytoken._parse_aws_key_trigger(request)
            canarydrop.add_canarydrop_hit(token_hit=token_hit)
            self.dispatch(canarydrop=canarydrop, token_hit=token_hit)
            return b"success"
        elif canarydrop.type == TokenTypes.AZURE_ID:
            token_hit = Canarytoken._parse_azure_id_trigger(request)
            canarydrop.add_canarydrop_hit(token_hit=token_hit)
            self.dispatch(canarydrop=canarydrop, token_hit=token_hit)
            return b"success"
        elif canarydrop.type == TokenTypes.SLACK_API:
            token_hit = Canarytoken._parse_slack_api_trigger(request)
            canarydrop.add_canarydrop_hit(token_hit=token_hit)
            self.dispatch(canarydrop=canarydrop, token_hit=token_hit)
            return b"success"
        elif canarydrop.type in [
            TokenTypes.SLOW_REDIRECT,
            TokenTypes.WEB_IMAGE,
            TokenTypes.WEB,
        ]:
            key = request.args.get(b"key", [None])[0]
            if (key := coerce_to_float(key)) and token:
                additional_info = {
                    k.decode(): v
                    for k, v in request.args.items()
                    if k.decode() not in ["key", "canarytoken", "name"]
                }
                canarydrop.add_additional_info_to_hit(
                    hit_time=key,
                    additional_info={
                        request.args[b"name"][0].decode(): additional_info
                    },
                )
                self.dispatch(
                    canarydrop=canarydrop,
                    token_hit=canarydrop.triggered_details.hits[-1],
                )
                return b"success"
            else:
                log.info(
                    f"Either {key=} or {token=} were falsy. Dropping this request."
                )
                # TODO: These returns are not really needed
                return b"failed"
        else:
            return self.render_GET(request)


class ChannelHTTP:
    def __init__(
        self,
        frontend_settings: FrontendSettings,
        switchboard_settings: SwitchboardSettings,
        switchboard: Switchboard,
    ):
        self.port = switchboard_settings.CHANNEL_HTTP_PORT

        self.canarytoken_page = CanarytokenPage(
            switchboard=switchboard,
            switchboard_hostname=frontend_settings.DOMAINS[0],
            switchboard_scheme=switchboard_settings.SWITCHBOARD_SCHEME,
        )
        wrapped = EncodingResourceWrapper(self.canarytoken_page, [GzipEncoderFactory()])
        self.site = server.Site(wrapped)
        self.service = internet.TCPServer(self.port, self.site)
        return None
