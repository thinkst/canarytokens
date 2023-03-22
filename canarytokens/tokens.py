from __future__ import annotations

import base64
import random
import re
from datetime import datetime
from functools import cache
from typing import Any, AnyStr, Match, Optional

from jinja2 import Environment, FileSystemLoader
from pydantic import parse_obj_as
from twisted.web.http import Request
from twisted.web.util import redirectTo

from canarytokens import canarydrop, queries
from canarytokens.constants import (
    CANARYTOKEN_ALPHABET,
    CANARYTOKEN_LENGTH,
    INPUT_CHANNEL_HTTP,
)
from canarytokens.exceptions import NoCanarytokenFound
from canarytokens.models import AnyTokenHit, AWSKeyTokenHit, TokenTypes

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
dtrace_process = re.compile(
    r"([0-9]+)\.([A-Za-z0-9-=]+)\.h\.([A-Za-z0-9.-=]+)\.c\.([A-Za-z0-9.-=]+)\.D1\.",
    re.IGNORECASE,
)
dtrace_file_open = re.compile(
    r"([0-9]+)\.([A-Za-z0-9-=]+)\.h\.([A-Za-z0-9.-=]+)\.f\.([A-Za-z0-9.-=]+)\.D2\.",
    re.IGNORECASE,
)
desktop_ini_browsing_pattern = re.compile(
    r"([^\.]+)\.([^\.]+)\.?([^\.]*)\.ini\.",
    re.IGNORECASE,
)
log4_shell_pattern = re.compile(r"([A-Za-z0-9.-]*)\.L4J\.", re.IGNORECASE)
cmd_process_pattern = re.compile(r"(.+)\.UN\.(.+)\.CMD\.", re.IGNORECASE)

GIF = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"  # 1x1 GIF

# TODO: we can do better than this.
# ??
source_data_extractors = {
    "sql_server_username": sql_server_username,
    "mysql_username": mysql_username,
    "linux_inotify": linux_inotify,
    "generic": generic,
    "dtrace_process": dtrace_process,
    "dtrace_file_open": dtrace_file_open,
    "desktop_ini_browsing": desktop_ini_browsing_pattern,
    "log4_shell": log4_shell_pattern,
    "cmd_process": cmd_process_pattern,
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
                value = value.decode()
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

    # @staticmethod
    # def _sql_server_data(matches: Match[AnyStr])->Dict[str, str]:
    #     match = matches.group(1)
    #     if isinstance(match, str):
    #         username:str = match
    #     elif isinstance(match,bytes):
    #         username:str = match.decode()
    #     else:
    #         username:str = ""
    #     data = {}
    #     # TODO: decoded base64 can contain all sorts of character
    #     # we need to sanitise this as it's user input!!!
    #     data["sql_username"] = base64.b64decode(
    #         username.replace(".", "").replace("-", "="),
    #     ).decode()
    #     return data

    # @staticmethod
    # def _mysql_data(matches: Match[AnyStr])->Dict[str,str]:
    #     match = matches.group(1)
    #     if isinstance(match, str):
    #         username:str = match
    #     elif isinstance(match,bytes):
    #         username:str = match.decode()
    #     else:
    #         username:str = ""
    #     data = {}
    #     # TODO: decoded base64 can contain all sorts of character
    #     # we need to sanitise this as it's user input!!!
    #     data["mysql_username"] = base64.b32decode(
    #         username.replace(".", "").replace("-", "=").upper(),
    #     ).decode()
    #     return data

    # @staticmethod
    # def _linux_inotify_data(matches: Match[AnyStr]) -> Dict[str, str]:
    #     data = {}
    #     filename = matches.group(1)
    #     filename = filename.replace(b".", b"").upper()
    #     # this channel doesn't have padding, add if needed
    #     filename += "=" * int((math.ceil(float(len(filename)) / 8) * 8 - len(filename)))
    #     data["linux_inotify_filename_access"] = base64.b32decode(filename)
    #     return data

    @staticmethod
    def _generic(matches: Match[AnyStr]) -> dict[str, str]:
        data = {}
        generic_data = matches.group(1)
        generic_data = generic_data.replace(".", "").upper()
        # this channel doesn't have padding, add if needed
        # TODO: put this padding logic into utils somewhere.
        generic_data_padded = generic_data.ljust(
            len(generic_data) + (-len(generic_data) % 8), "="
        )
        try:
            # TODO: this can smuggle in all sorts of data we need to sanitise
            #
            data["generic_data"] = base64.b32decode(generic_data_padded)
        except TypeError:
            data["generic_data"] = f"Unrecoverable data: {generic_data_padded}"
        return {"src_data": data}

    @staticmethod
    def _dtrace_process_data(matches: Match[AnyStr]) -> dict[str, str]:
        raise NotImplementedError("Please implement me! ")
        # data = {}
        # try:
        #     data['dtrace_uid'] = base64.b64decode(uid)
        # except:
        #     log.error(
        #         'Could not retrieve uid from dtrace '
        #         + 'process alert: {uid}'.format(uid=uid),
        #     )
        # try:
        #     data['dtrace_hostname'] = base64.b64decode(hostname.replace('.', ''))
        # except:
        #     log.error(
        #         'Could not retrieve hostname from dtrace '
        #         + 'process alert: {hostname}'.format(hostname=hostname),
        #     )
        # try:
        #     data['dtrace_command'] = base64.b64decode(command.replace('.', ''))
        # except:
        #     log.error(
        #         'Could not retrieve command from dtrace '
        #         + 'process alert: {command}'.format(command=command),
        #     )

        # return data

    @staticmethod
    def _dtrace_file_open(matches: Match[AnyStr]) -> dict[str, str]:
        raise NotImplementedError("Please implement me")
        # data = {}
        # try:
        #     data['dtrace_uid'] = base64.b64decode(uid)
        # except:
        #     log.error(
        #         'Could not retrieve uid from dtrace '
        #         + 'file open alert: {uid}'.format(uid=uid),
        #     )

        # try:
        #     data['dtrace_hostname'] = base64.b64decode(hostname.replace('.', ''))
        # except:
        #     log.error(
        #         'Could not retrieve hostname from dtrace '
        #         + 'process alert: {hostname}'.format(hostname=hostname),
        #     )
        # try:
        #     data['dtrace_filename'] = base64.b64decode(filename.replace('.', ''))
        # except:
        #     log.error(
        #         'Could not retrieve filename from dtrace '
        #         + 'file open alert: {filename}'.format(filename=filename),
        #     )

        # return data

    @staticmethod
    def _cmd_process(matches: Match[AnyStr]) -> dict[str, dict[str, AnyStr]]:
        """"""
        computer_name = matches.group(1)
        user_name = matches.group(2)
        data = {}
        data["cmd_computer_name"] = "Not Obtained"
        data["cmd_user_name"] = "Not Obtained"
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
                "windows_desktopini_access_username": username,
                "windows_desktopini_access_hostname": hostname,
                "windows_desktopini_access_domain": domain,
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
            computer_name = "Not Obtained"
        else:
            computer_name = computer_name[1:]
        data["src_data"] = {"log4_shell_computer_name": computer_name}
        return data

    @staticmethod
    def _grab_http_general_info(request: Request):
        """"""
        useragent = request.getHeader("User-Agent") or "No useragent specified"
        src_ip = request.getHeader("x-real-ip") or request.client.host
        # DESIGN/TODO: this makes a call to third party ensure we happy with fails here
        #              and have default.
        is_tor_relay = queries.is_tor_relay(src_ip)
        src_ips = request.getHeader("x-forwarded-for") or ""
        # TODO: Check how typical clients use 'x-forwarded-for'
        src_ip_chain = [o.strip() for o in src_ips.split(",")]
        # TODO: 'ts_key' -> which tokens fire this?
        hit_time = request.args.get("ts_key", [datetime.utcnow().strftime("%s")])[0]
        flatten_singletons = lambda l: l[0] if len(l) == 1 else l  # noqa: E731
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
            hit_info = {
                "token_type": TokenTypes.AWS_KEYS,
                "safety_net": True,
                "time_of_hit": hit_time,
                "input_channel": INPUT_CHANNEL_HTTP,
            }
        else:
            hit_time = data.get("ts_key", [datetime.utcnow().strftime("%s")])[0]
            # the source IP here is the one AWS sends, not the one belonging to them
            src_ip = data["ip"][0]
            # DESIGN/TODO: this makes a call to third party ensure we happy with fails here
            #              and have default.
            geo_info = queries.get_geoinfo_from_ip(ip=src_ip)
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
    def _get_info_for_fast_redirect(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        return http_general_info, {}

    @staticmethod
    def _get_response_for_fast_redirect(
        canarydrop: canarydrop.Canarydrop, request: Request
    ):
        return redirectTo(str(canarydrop.redirect_url).encode(), request)

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
        template = get_template_env().get_template("browser_scanner.html")
        return template.render(
            key=canarydrop.triggered_details.hits[-1].time_of_hit,
            canarytoken=canarydrop.canarytoken.value(),
            redirect_url=str(canarydrop.redirect_url).encode("utf8"),
        ).encode()

    @staticmethod
    def _get_info_for_web(request):
        http_general_info = Canarytoken._grab_http_general_info(request=request)
        return http_general_info, {}

    @staticmethod
    def _get_response_for_web(
        canarydrop: canarydrop.Canarydrop, request: Request
    ) -> bytes:
        if canarydrop.browser_scanner_enabled:
            template = get_template_env().get_template("browser_scanner.html")
            return template.render(
                key=canarydrop.triggered_details.hits[-1].time_of_hit,
                canarytoken=canarydrop.canarytoken.value(),
            ).encode()
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
            geo_info = queries.get_geoinfo_from_ip(ip=src_ip)
            is_tor_relay = queries.is_tor_relay(src_ip)
        hit_info["geo_info"] = geo_info
        hit_info["is_tor_relay"] = is_tor_relay

        return parse_obj_as(
            AnyTokenHit,
            hit_info,
        )
