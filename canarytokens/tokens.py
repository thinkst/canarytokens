from __future__ import annotations

import base64
import binascii
import json
import random
import re
from datetime import datetime
from functools import cache
from typing import Any, AnyStr, Match, Optional

from jinja2 import Environment, FileSystemLoader
from pydantic import parse_obj_as
from twisted.web.http import Request
from twisted.web.util import redirectTo

from canarytokens.settings import SwitchboardSettings

from canarytokens import canarydrop, queries
from canarytokens.constants import (
    CANARYTOKEN_ALPHABET,
    CANARYTOKEN_LENGTH,
    INPUT_CHANNEL_HTTP,
)
from canarytokens.exceptions import NoCanarytokenFound
from canarytokens.models import (
    AnyTokenHit,
    AWSKeyTokenHit,
    AzureIDTokenHit,
    SlackAPITokenHit,
    TokenTypes,
)

# TODO: put these in a nicer place. Ensure re.compile is called only once at startup
# add a naming convention for easy reading when seen in other files.
# Check that state is not stored in these eg: x=re.compile(...) x.match() === A and then x.match() === A still
sql_server_username = re.compile(
    r"([A-Za-z0-9.-]*)\.[0-9]{2}\.",
    re.IGNORECASE,
)
mysql_username = re.compile(r"([A-Za-z0-9.-]*)\.M[0-9]{3}\.", re.IGNORECASE)
linux_inotify = re.compile(r"([A-Za-z0-9.-]*)\.L[0-9]{2}\.", re.IGNORECASE)
generic = re.compile(r"([A-Z2-7.-]*)\.G[0-9]{2}\.", re.IGNORECASE)
desktop_ini_browsing_pattern = re.compile(
    r"([^\.]+)\.([^\.]+)\.?([^\.]*)\.ini\.",
    re.IGNORECASE,
)
log4_shell_pattern = re.compile(r"([A-Za-z0-9.-]*)\.L4J\.", re.IGNORECASE)
cmd_process_pattern = re.compile(r"(.+)\.UN\.(.+)\.CMD\.", re.IGNORECASE)

# to validate decoded sql username, not a data extractor:
sql_decoded_username = re.compile(r"[A-Za-z0-9\!\#\'\-\.\\\^\_\~]+")
GIF = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"  # 1x1 GIF

# TODO: we can do better than this.
# ??
source_data_extractors = {
    "linux_inotify": linux_inotify,
    "generic": generic,
    "desktop_ini_browsing": desktop_ini_browsing_pattern,
    "log4_shell": log4_shell_pattern,
    "cmd_process": cmd_process_pattern,
    "sql_server_username": sql_server_username,
}

# DESIGN: keeping the lib and apps separate called for some
#         non-ideal things. Ideas?
# get_template_env = None

g_template_dir: Optional[str]


def set_template_env(template_dir):
    global g_template_dir
    g_template_dir = template_dir


@cache
def get_template_env():
    global g_template_dir
    if g_template_dir is None:
        raise ValueError("g_template_dir must be set via tokens.set_template_env(...)")
    return Environment(loader=FileSystemLoader(g_template_dir))


class Canarytoken(object):
    CANARY_RE = re.compile(
        ".*(["
        + "".join(CANARYTOKEN_ALPHABET)
        + "]{"
        + str(CANARYTOKEN_LENGTH)
        + "}).*",
        re.IGNORECASE,
    )

    def __init__(self, value: Optional[AnyStr] = None):
        """Create a new Canarytoken instance. If no value was provided,
        generate a new canarytoken.

        Arguments:
        value -- A user-provided canarytoken. It's format will be validated.

        Exceptions:
        NoCanarytokenFound - Thrown if the supplied canarytoken is not in the
                           correct format.
        """
        if value:
            if isinstance(value, bytes):
                try:
                    value = value.decode()
                except UnicodeDecodeError:
                    raise NoCanarytokenFound(f"Non-decodable bytes found: {value}")
            self._value = self.find_canarytoken(value).lower()
        else:
            self._value = Canarytoken.generate()

    @staticmethod
    def generate() -> str:
        """Return a new canarytoken."""
        return "".join(
            [random.choice(CANARYTOKEN_ALPHABET) for x in range(0, CANARYTOKEN_LENGTH)],
        )

    @staticmethod
    def find_canarytoken(haystack: str) -> str:
        """Return the canarytoken found in haystack.

        Arguments:
        haystack -- A string that might include a canarytoken.

        Exceptions:
        NoCanarytokenFound
        """
        m = Canarytoken.CANARY_RE.match(haystack)
        if not m:
            raise NoCanarytokenFound(haystack)

        return m.group(1)

    def value(
        self,
    ):
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Canarytoken):
            return self.value() == other.value()
        return False

    @staticmethod
    def look_for_source_data(query_name: str) -> dict[str, str]:
        for source_name, source_extractor in source_data_extractors.items():
            if (m := source_extractor.match(query_name)) is not None:
                return getattr(Canarytoken, f"_{source_name}")(m)
        else:
            return {}

    @staticmethod
    def _sql_server_username(matches: Match[AnyStr]) -> dict[str, str]:
        match = matches.group(1)
        if isinstance(match, str):
            raw_username: str = match
        elif isinstance(match, bytes):
            raw_username: str = match.decode()
        else:
            raw_username: str = ""
        data = {}
        try:
            decoded_username = base64.b64decode(
                raw_username.replace(".", "").replace("-", "="),
            ).decode()
            username_matches = sql_decoded_username.match(decoded_username)
            if username_matches:
                data["sql_username"] = username_matches.group()
            else:
                data["sql_username"] = f"Decoded base-64: {decoded_username}"
        except Exception:
            data["sql_username"] = f"Failed to decode. Received: {raw_username}"

        return {"src_data": data} if data else {}

    @staticmethod
    def _linux_inotify(matches: Match[AnyStr]) -> dict[str, str]:
        match = matches.group(1)
        if isinstance(match, str):
            filename: str = match.encode()
        elif isinstance(match, bytes):
            filename: str = match
        else:
            filename: str = b""
        data = {}
        filename = filename.replace(b".", b"").upper()
        # this channel doesn't have padding, add if needed
        filename += b"=" * ((8 - len(filename)) % 8)
        data["linux_inotify_filename_access"] = base64.b32decode(filename)
        return {"src_data": data} if data else {}

    @staticmethod
    def _generic(matches: Match[AnyStr]) -> dict[str, str]:
        data = {}
        incoming_data = matches.group(1)
        generic_data = incoming_data.replace(".", "").replace("-", "=").upper()
        # this channel doesn't have padding, add if needed
        # TODO: put this padding logic into utils somewhere.
        generic_data_padded = generic_data.ljust(
            len(generic_data) + (-len(generic_data) % 8), "="
        )
        try:
            # TODO: this can smuggle in all sorts of data we need to sanitise
            #
            raw_bytes = base64.b32decode(generic_data_padded)
            try:
                data["generic_data"] = raw_bytes.decode()
            except UnicodeDecodeError:
                data["generic_data"] = binascii.hexlify(raw_bytes).decode()
        except (TypeError, binascii.Error):
            data["generic_data"] = f"Unrecoverable data: {incoming_data}"
        return {"src_data": data}

    @staticmethod
    def _cmd_process(matches: Match[AnyStr]) -> dict[str, dict[str, AnyStr]]:
        """"""
        computer_name = matches.group(1).lower()
        user_name = matches.group(2).lower()
        data = {}
        data["cmd_computer_name"] = "(not obtained)"
        data["cmd_user_name"] = "(not obtained)"
        if user_name and user_name != "u":
            data["cmd_user_name"] = user_name[1:]
        if computer_name and computer_name != "c":
            data["cmd_computer_name"] = computer_name[1:]
        return {"src_data": data}

    @staticmethod
    def _desktop_ini_browsing(matches: Match[AnyStr]) -> dict[str, dict[str, AnyStr]]:
        username = matches.group(1)
        hostname = matches.group(2)
        domain = matches.group(3)
        return {
            "src_data": {
                "windows_desktopini_access_username": username.lower(),
                "windows_desktopini_access_hostname": hostname.lower(),
                "windows_desktopini_access_domain": domain.lower(),
            }
        }

    @staticmethod
    def _log4_shell(matches: Match[AnyStr]) -> dict[str, dict[str, str]]:
        data = {}
        computer_name = matches.group(1)
        if isinstance(computer_name, bytes):
            computer_name = computer_name.decode()

        # TODO: refactor (make nice) and make 'x' a variable eg: _l4j_hostname_marker.
        if len(computer_name) <= 1 or not computer_name.startswith("x"):
            computer_name = "(not obtained)"
        else:
            computer_name = computer_name[1:]
        data["src_data"] = {"log4_shell_computer_name": computer_name}
        return data

    @staticmethod
    def _grab_http_general_info(request: Request):
        """"""
        useragent = request.getHeader("User-Agent") or "(no user-agent specified)"
        switchboard_settings = SwitchboardSettings()
        src_ip = (
            request.getHeader(switchboard_settings.REAL_IP_HEADER)
            or request.client.host
        )
        # DESIGN/TODO: this makes a call to third party ensure we happy with fails here
        #              and have default.
        is_tor_relay = queries.is_tor_relay(src_ip)
        src_ips = request.getHeader("x-forwarded-for") or ""
        # TODO: Check how typical clients use 'x-forwarded-for'
        src_ip_chain = [o.strip() for o in src_ips.split(",")]
        # TODO: 'ts_key' -> which tokens fire this?
        hit_time = request.args.get("ts_key", [datetime.utcnow().strftime("%s.%f")])[0]
        flatten_singletons = lambda d: d[0] if len(d) == 1 else d  # noqa: E731
        request_headers = {
            k.decode(): flatten_singletons([s.decode() for s in v])
            for k, v in request.requestHeaders.getAllRawHeaders()
        }
        request_args = (
            {
                k.decode(): ",".join([s.decode() for s in v])
                for k, v in request.args.items()
            }
            if isinstance(request.args, dict)
            else {}
        )
        return {
            "useragent": useragent,
            "x_forwarded_for": src_ip_chain,
            "src_ip": src_ip,
            "time_of_hit": hit_time,
            "is_tor_relay": is_tor_relay,
            "request_headers": request_headers,
            "request_args": request_args,
        }

    @staticmethod
    def _parse_aws_key_trigger(
        request: Request,
    ) -> AWSKeyTokenHit:
        """When an AWSKey token is triggered a lambda makes a POST request
        back to switchboard. The `request` is processed, fields extracted,
        and an `AWSKeyTokenHit` is created.

        Args:
            request (twisted.web.http.Request): containing AWS Key hit information.

        Returns:
            AWSKeyTokenHit: Structured AWS Key Specific hit info.
        """
        data: dict[str, list[str]] = {
            k.decode(): [o.decode() for o in v] for k, v in request.args.items()
        }

        if "safety_net" in data and data["safety_net"][0] == "True":
            timestamp = data["last_used"][0]
            hit_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z").strftime(
                "%s"
            )
            service_used = data["last_used_service"][0]

            hit_info = {
                "token_type": TokenTypes.AWS_KEYS,
                "safety_net": True,
                "time_of_hit": hit_time,
                "service_used": service_used,
                "input_channel": INPUT_CHANNEL_HTTP,
            }
        else:
            hit_time = data.get("ts_key", [datetime.utcnow().strftime("%s.%f")])[0]
            # the source IP here is the one AWS sends, not the one belonging to them
            src_ip = data["ip"][0]
            # DESIGN/TODO: this makes a call to third party ensure we happy with fails here
            #              and have default.
            geo_info = queries.get_geoinfo(ip=src_ip)
            is_tor_relay = queries.is_tor_relay(src_ip)
            user_agent = data["user_agent"][0]
            hit_info = {
                "token_type": TokenTypes.AWS_KEYS,
                "time_of_hit": hit_time,
                "input_channel": INPUT_CHANNEL_HTTP,
                "src_ip": src_ip,
                "geo_info": geo_info,
                "is_tor_relay": is_tor_relay,
                "user_agent": user_agent,
                "additional_info": {
                    "aws_key_log_data": {
                        k: v for k, v in data.items() if k not in ["ip", "user_agent"]
                    }
                },
            }
        return AWSKeyTokenHit(**hit_info)

    @staticmethod
    def _parse_azure_id_trigger(
        request: Request,
    ) -> AzureIDTokenHit:
        """When an AzureID token is triggered, Azure makes a POST request
        back to switchboard. The `request` is processed, fields extracted,
        and an `AzureIDTokenHit` is created.

        Args:
            request (twisted.web.http.Request): containing Azure Key hit information.

        Returns:
            AzureIDTokenHit: Structured Azure Key Specific hit info.
        """

        hit_time = datetime.utcnow().strftime("%s.%f")

        json_data = json.loads(request.content.read())
        src_ip = json_data.get("ip", "127.0.0.1")

        auth_details = json_data.get("auth_details", "")
        if type(auth_details) is list:
            out = ""
            for d in auth_details:
                out += "\n{}: {}".format(d["key"], d["value"])
            auth_details = out

        location_details = json_data.get("location", {})
        geo_details = location_details.get("geoCoordinates", {})

        additional_info = {
            "Azure ID Log Data": {
                "Date": [json_data.get("time", "(not available)")],
                "Authentication": [auth_details],
            },
            "Microsoft Azure": {
                "Resource": [json_data.get("resource", "(not available)")],
                "App ID": [json_data.get("app_id", "(not available)")],
                "Cert ID": [json_data.get("cert_id", "(not available)")],
            },
            "Location": {
                "city": [location_details.get("city", "(not available)")],
                "state": [location_details.get("state", "(not available)")],
                "countryOrRegion": [
                    location_details.get("countryOrRegion", "(not available)")
                ],
            },
            "Coordinates": {
                "latitude": [geo_details.get("latitude", "(not available)")],
                "longitude": [geo_details.get("longitude", "(not available)")],
            },
        }
        hit_info = {
            "token_type": TokenTypes.AZURE_ID,
            "time_of_hit": hit_time,
            "input_channel": INPUT_CHANNEL_HTTP,
            "src_ip": src_ip,
            # "geo_info": geo_info,
            # "is_tor_relay": is_tor_relay,
            # "user_agent": user_agent,
            "additional_info": additional_info,
        }
        return AzureIDTokenHit(**hit_info)

    @staticmethod
    def _parse_slack_api_trigger(request):
        data = {k.decode(): [o.decode() for o in v] for k, v in request.args.items()}
        hit_time = datetime.utcnow().strftime("%s.%f")
        src_ip = data["ip"][0]
        geo_info = queries.get_geoinfo(ip=src_ip)
        is_tor_relay = queries.is_tor_relay(src_ip)
        user_agent = data["user_agent"][0]
        hit_info = {
            "token_type": TokenTypes.SLACK_API,
            "time_of_hit": hit_time,
            "input_channel": INPUT_CHANNEL_HTTP,
            "src_ip": src_ip,
            "geo_info": geo_info,
            "is_tor_relay": is_tor_relay,
            "user_agent": user_agent,
            "additional_info": {
                "Slack Log Data": {
                    k: v for k, v in data.items() if k not in ["ip", "user_agent"]
                }
            },
        }
        return SlackAPITokenHit(**hit_info)

    @staticmethod
    def _get_info_for_clonedsite(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)

        location = request.args.get(b"l", [None])[0]
        referer = request.args.get(b"r", [None])[0]
        src_data = {
            "location": location,
            "referer": referer,
        }
        return http_general_info, src_data

    @staticmethod
    def _get_response_for_clonedsite(
        canarydrop: canarydrop.Canarydrop, request: Request
    ):
        request.setHeader("Content-Type", "image/gif")
        return GIF

    @staticmethod
    def _get_info_for_cssclonedsite(request: Request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)

        referer = request.getHeader('Referer')
        src_data = {
            "referer": referer,
            "location": referer,
        }
        return http_general_info, src_data

    @staticmethod
    def _get_response_for_cssclonedsite(
        canarydrop: canarydrop.Canarydrop, request: Request
    ):
        request.setHeader("Content-Type", "image/gif")
        return GIF

    @staticmethod
    def _get_info_for_cc(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)

        last4 = request.getHeader("Last4")
        amount = "$" + request.getHeader("Amount")
        merchant = request.getHeader("Merchant")

        # TODO: check if we need to nerf geo_info, src_ip and is_tor_relay
        #       from http_general_info
        src_data = {"last4": last4, "amount": amount, "merchant": merchant}
        return http_general_info, src_data

    @staticmethod
    def _get_response_for_cc(canarydrop: canarydrop.Canarydrop, request: Request):
        request.setHeader("Content-Type", "image/gif")
        return GIF

    @staticmethod
    def _get_info_for_fast_redirect(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        return http_general_info, {}

    @staticmethod
    def _get_response_for_fast_redirect(
        canarydrop: canarydrop.Canarydrop, request: Request
    ):
        redirect_url = canarydrop.redirect_url
        if redirect_url:
            if ":" not in redirect_url:
                redirect_url = "http://" + redirect_url
            return redirectTo(redirect_url.encode(), request)
        return GIF

    @staticmethod
    def _get_info_for_slow_redirect(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        location = request.args.get(b"l", [None])[0]
        referer = request.args.get(b"r", [None])[0]
        src_data = {
            "location": location,
            "referer": referer,
        }
        return http_general_info, src_data

    @staticmethod
    def _get_response_for_slow_redirect(
        canarydrop: canarydrop.Canarydrop, request: Request
    ) -> bytes:
        redirect_url = canarydrop.redirect_url
        if redirect_url and ":" not in redirect_url:
            redirect_url = "http://" + redirect_url
        template = get_template_env().get_template("browser_scanner.html")
        return template.render(
            key=canarydrop.triggered_details.hits[-1].time_of_hit,
            canarytoken=canarydrop.canarytoken.value(),
            redirect_url=redirect_url,
        ).encode()

    @staticmethod
    def _get_info_for_web(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        return http_general_info, {}

    @staticmethod
    def _get_response_for_web(
        canarydrop: canarydrop.Canarydrop, request: Request
    ) -> bytes:
        if request.getHeader("Accept") and "text/html" in request.getHeader("Accept"):
            if canarydrop.browser_scanner_enabled:
                # set response mimetype
                request.setHeader("Content-Type", "text/html")
                # latest hit
                latest_hit_time = canarydrop.triggered_details.hits[-1].time_of_hit
                # set-up response template
                browser_scanner_template_params = {
                    "key": latest_hit_time,
                    "canarytoken": canarydrop.canarytoken.value,
                    "redirect_url": "",
                }
                template = get_template_env().get_template("browser_scanner.html")
                # render template
                return template.render(**browser_scanner_template_params).encode()

            elif queries.get_return_for_token() == "fortune":  # gif
                # set response mimetype
                request.setHeader("Content-Type", "text/html")

                # get fortune
                # fortune = subprocess.check_output('/usr/games/fortune')
                fortune = "fortune favours the brave"

                # set-up response template
                fortune_template_params = {"request": request, "fortune": fortune}
                template = get_template_env().get_template("fortune.html")

                # render template
                return template.render(**fortune_template_params).encode()

        request.setHeader("Content-Type", "image/gif")
        return GIF

    @staticmethod
    def _get_info_for_qr_code(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        return http_general_info, {"useragent": http_general_info["useragent"]}

    @staticmethod
    def _get_response_for_qr_code(
        canarydrop: canarydrop.Canarydrop, request: Request
    ) -> bytes:
        request.setHeader("Content-Type", "image/gif")
        return GIF

    @staticmethod
    def _get_info_for_ms_word(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        return http_general_info, {}

    @staticmethod
    def _get_response_for_ms_word(canarydrop: canarydrop.Canarydrop, request: Request):
        request.setHeader("Content-Type", "image/gif")
        return GIF

    @staticmethod
    def _get_info_for_ms_excel(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        return http_general_info, {}

    @staticmethod
    def _get_response_for_ms_excel(canarydrop: canarydrop.Canarydrop, request: Request):
        request.setHeader("Content-Type", "image/gif")
        return GIF

    @staticmethod
    def _get_info_for_web_image(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        return http_general_info, {}

    @staticmethod
    def _get_response_for_web_image(
        canarydrop: canarydrop.Canarydrop, request: Request
    ):
        if request.getHeader("Accept") and "text/html" in request.getHeader("Accept"):
            if canarydrop.browser_scanner_enabled:
                # set response mimetype
                request.setHeader("Content-Type", "text/html")
                # latest hit
                latest_hit_time = canarydrop.triggered_details.hits[-1].time_of_hit
                # set-up response template
                browser_scanner_template_params = {
                    "key": latest_hit_time,
                    "canarytoken": canarydrop.canarytoken.value,
                    "redirect_url": "",
                }
                template = get_template_env().get_template("browser_scanner.html")
                # render template
                return template.render(**browser_scanner_template_params).encode()

            elif queries.get_return_for_token() == "fortune":  # gif
                # set response mimetype
                request.setHeader("Content-Type", "text/html")

                # get fortune
                # fortune = subprocess.check_output('/usr/games/fortune')
                fortune = "fortune favours the brave"

                # set-up response template
                fortune_template_params = {"request": request, "fortune": fortune}
                template = get_template_env().get_template("fortune.html")

                # render template
                return template.render(**fortune_template_params).encode()

        _check_and_add_cors_headers(request)

        if canarydrop.web_image_enabled and canarydrop.web_image_path.exists():
            # set response mimetype
            mimetype = "image/{mime}".format(mime=canarydrop.web_image_path.suffix[-3:])
            request.setHeader("Content-Type", mimetype)
            # read custom image
            with canarydrop.web_image_path.open(mode="rb") as fp:
                contents = fp.read()
            return contents

        request.setHeader("Content-Type", "image/gif")
        return GIF

    @staticmethod
    def _get_info_for_legacy(request):
        """
        Since we don't know what type legacy tokens are, we attempt to collect all the data that could be there. The token types that alert here are:
            web, MS Word, custom image, QR code, and cloned site
        """
        # web, word, image
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        src_data = {}
        # QR
        if "useragent" in http_general_info:
            src_data["useragent"] = http_general_info["useragent"]
        # cloned
        if location := request.args.get(b"l", [None])[0]:
            src_data["location"] = location
        if referer := request.args.get(b"r", [None])[0]:
            src_data["referer"] = referer
        return http_general_info, src_data

    @staticmethod
    def _get_response_for_legacy(canarydrop: canarydrop.Canarydrop, request: Request):
        """
        Since we don't know what type legacy tokens are, we need to derive the correct response here.
        The token types that we could be responding for are:
            web, MS Word, custom image, QR code, and cloned site
        They all respond with a GIF except in the same conditions as the custom image token, so that functionality is replicated here
        """

        if request.getHeader("Accept") and "text/html" in request.getHeader("Accept"):
            if canarydrop.browser_scanner_enabled:
                # set response mimetype
                request.setHeader("Content-Type", "text/html")
                # latest hit
                latest_hit_time = canarydrop.triggered_details.hits[-1].time_of_hit
                # set-up response template
                browser_scanner_template_params = {
                    "key": latest_hit_time,
                    "canarytoken": canarydrop.canarytoken.value,
                    "redirect_url": "",
                }
                template = get_template_env().get_template("browser_scanner.html")
                # render template
                return template.render(**browser_scanner_template_params).encode()

            elif queries.get_return_for_token() == "fortune":  # gif
                # set response mimetype
                request.setHeader("Content-Type", "text/html")

                # get fortune
                # fortune = subprocess.check_output('/usr/games/fortune')
                fortune = "fortune favours the brave"

                # set-up response template
                fortune_template_params = {"request": request, "fortune": fortune}
                template = get_template_env().get_template("fortune.html")

                # render template
                return template.render(**fortune_template_params).encode()

        if canarydrop.web_image_enabled and canarydrop.web_image_path.exists():
            # set response mimetype
            mimetype = "image/{mime}".format(mime=canarydrop.web_image_path.suffix[-3:])
            request.setHeader("Content-Type", mimetype)
            # read custom image
            with canarydrop.web_image_path.open(mode="rb") as fp:
                contents = fp.read()
            return contents

        request.setHeader("Content-Type", "image/gif")
        return GIF

    @staticmethod
    def create_token_hit(
        token_type,
        *,
        input_channel: str,
        src_ip: Optional[str],
        hit_info: dict[str, Any],
        time_of_hit: Optional[str] = None,
    ):
        # DESIGN: we can do better. Dispatch on token_type.
        time_of_hit = time_of_hit or datetime.utcnow().strftime("%s.%f")
        # DESIGN/TODO: 3rd party reliance here. we need to see how we fail safe here.
        hit_info["time_of_hit"] = time_of_hit
        hit_info["token_type"] = token_type
        hit_info["input_channel"] = input_channel

        geo_info = None
        is_tor_relay = None
        if src_ip and ("safety_net" not in hit_info or not hit_info["safety_net"]):
            hit_info["src_ip"] = src_ip
            geo_info = queries.get_geoinfo(ip=src_ip)
            is_tor_relay = queries.is_tor_relay(src_ip)
        hit_info["geo_info"] = geo_info
        hit_info["is_tor_relay"] = is_tor_relay

        return parse_obj_as(
            AnyTokenHit,
            hit_info,
        )


def _check_and_add_cors_headers(request: Request):
    """
    According to https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request, we
    should check for `Access-Control-Request-Method` and `Origin` and optionally,
    `Access-Control-Request-Headers` headers in an OPTIONS request to determine its a preflight request; and
    respond with `Access-Control-Allow-Origin` and `Access-Control-Allow-Methods`. Else, we
    will add `Access-Control-Allow-Origin: *` to the GET request.
    """
    if request.method.upper() == b"GET":
        request.setHeader("Access-Control-Allow-Origin", "*")
    elif request.method.upper() == b"OPTIONS":
        if (
            request.getHeader("Access-Control-Request-Method") is None
            or request.getHeader("Origin") is None
        ):
            return

        acr_headers = request.getHeader("Access-Control-Request-Headers")
        if acr_headers is not None:
            request.setHeader("Access-Control-Allow-Headers", acr_headers)

        request.setHeader("Access-Control-Allow-Origin", request.getHeader("Origin"))
        request.setHeader("Access-Control-Allow-Methods", "OPTIONS, GET, POST")
