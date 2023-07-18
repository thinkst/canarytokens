"""
A Canarydrop ties a canarytoken to an alerting mechanisms,
and records accounting information about the Canarytoken.

Maps to the object stored in Redis.
"""
from __future__ import annotations

import csv
import io
import json
import logging
import random
import textwrap
from base64 import b64encode
from datetime import datetime, timedelta
from hashlib import md5
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, EmailStr, Field, HttpUrl, parse_obj_as, root_validator

from canarytokens import queries, tokens
from canarytokens.constants import (
    OUTPUT_CHANNEL_EMAIL,
    OUTPUT_CHANNEL_TWILIO_SMS,
    OUTPUT_CHANNEL_WEBHOOK,
)
from canarytokens.models import (
    Anonymous,
    AnySettingsRequest,
    AnyTokenHistory,
    AnyTokenHit,
    BrowserScannerSettingsRequest,
    EmailSettingsRequest,
    TokenTypes,
    User,
    WebhookSettingsRequest,
    WebImageSettingsRequest,
)

logger = logging.getLogger(__name__)


def make_auth_token():
    """Generates an auth token that is associated 1 to 1 with a token."""
    # DESIGN: md5 hash? should we use something else?
    #
    return md5(
        str(
            random.SystemRandom().randrange(start=1, stop=2**128, step=2),
        ).encode(),
    ).hexdigest()


class Canarydrop(BaseModel):
    """
    Canarydrop links a Canarytoken to its alert and user details.
    Canarydrops serialize and are stored in Redis.
    """

    # Design: Model drops per type? Currently a Canarydrop has a `type` attribute making it
    #         tricker to use as it requires introspection before certain operations are performed.
    #         It may be simpler to break these up. See: _validate_redirect_url  and comments
    #         with ... stuff etc as motivation.

    generate: Optional[bool]  # V2 stores this attribute in redis.
    canarytoken: tokens.Canarytoken
    triggered_details: AnyTokenHistory
    memo: str
    # Make created_at v2 compatible - add timestamp as alias.
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="timestamp")

    auth: str = Field(default_factory=make_auth_token)
    type: TokenTypes
    user: Union[User, Anonymous] = Anonymous()

    token_url: Optional[str]
    generated_url: Optional[str]
    generated_hostname: Optional[str]

    # Alerting details
    alert_email_enabled: bool = False
    alert_email_recipient: Union[EmailStr, None, Literal[""]]
    alert_sms_enabled: bool = False
    # TODO: validate sms number
    alert_sms_recipient: Optional[str] = None
    alert_webhook_enabled: bool = False
    alert_webhook_url: Union[HttpUrl, None, Literal[""]]

    # web image specific stuff
    web_image_enabled: Optional[bool]
    web_image_path: Optional[Path]
    # Slow/Fast redirect specific stuff
    redirect_url: Optional[HttpUrl]
    # Clonedsite specific stuff
    clonedsite: Optional[HttpUrl]
    # Kubeconfig specific stuff
    kubeconfig: Optional[str]
    # SQL specific stuff
    sql_server_sql_action: Optional[Literal["INSERT", "DELETE", "UPDATE", "SELECT"]]
    sql_server_table_name: Optional[str]
    sql_server_view_name: Optional[str]
    sql_server_function_name: Optional[str]
    sql_server_trigger_name: Optional[str]
    # Custom upload stuff.
    file_contents: Optional[str]
    file_name: Optional[str]

    # AWS key specific stuff
    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]
    aws_output: Optional[str] = Field(alias="output")
    aws_region: Optional[str] = Field(alias="region")
    # HTTP style token specific stuff
    browser_scanner_enabled: Optional[bool]
    # Wireguard specific stuff
    wg_key: Optional[str]

    @root_validator(pre=True)
    def _validate_triggered_details(cls, values):
        """
        Ensure canarydrop `type` and `triggered_details` `token_type` match.
        """

        if values.get("triggered_details", None) is None:
            values["triggered_details"] = parse_obj_as(
                AnyTokenHistory, {"token_type": values["type"], "hits": []}
            )
        else:
            values["triggered_details"] = parse_obj_as(
                AnyTokenHistory, values["triggered_details"]
            )

        # Check that the triggered_details 'token_type' matches the 'type' of the canarydrop.
        if getattr(values["triggered_details"], "token_type") != values["type"]:
            raise ValueError(
                f"""trigger_details type must match drop type. Got:
            {getattr(values["triggered_details"], "token_type")} != {values["type"]}
            """
            )
        return values

    @root_validator(pre=True)
    def _validate_redirect_url(cls, values):
        """
        Ensure redirect url is present if it's a fast or
        slow redirect drop.
        """
        if values["type"] in [TokenTypes.FAST_REDIRECT, TokenTypes.SLOW_REDIRECT]:
            if not values.get("redirect_url", None):
                raise ValueError(f"redirect_url is required for {values['type']} drop")
        else:
            values.pop("redirect_url", None)
        return values

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.strftime("%s.%f"),
        }

    def add_additional_info_to_hit(
        self,
        hit_time: str,
        additional_info: Dict[str, str],
    ) -> None:
        """ """
        trigger_details = queries.get_canarydrop_triggered_details(self.canarytoken)
        if not any([hit_time == o.time_of_hit for o in trigger_details.hits]):
            raise ValueError(
                textwrap.dedent(
                    """
                Got additional details for a hit that does not exist.
                This is likely a use case we don't support yet but can.
            """
                )
            )

        queries.add_additional_info_to_hit(self.canarytoken, hit_time, additional_info)

    def add_canarydrop_hit(self, *, token_hit: AnyTokenHit):
        """Adds a hit to the drops history `.triggered_details`.

        Args:
            token_hit (AnyTokenHit): Hit to add.
        """
        queries.save_canarydrop(self)

        self.triggered_details.hits.append(token_hit)

        queries.add_canarydrop_hit(
            token_hit=token_hit,
            canarytoken=self.canarytoken,
        )

    def apply_settings_change(self, setting_request: AnySettingsRequest) -> bool:
        """
        Modifies a the drop applying (enable/disable) on any one
        of the settings.

        Args:
            setting_request (AnySettingsRequest): Setting to modify.

        Returns:
            bool: True if a supported setting. False otherwise.
        """
        if isinstance(setting_request, EmailSettingsRequest):
            self.alert_email_enabled = setting_request.value == "on"
        elif isinstance(setting_request, WebImageSettingsRequest):
            self.web_image_enabled = setting_request.value == "on"
        elif isinstance(setting_request, WebhookSettingsRequest):
            self.alert_webhook_enabled = setting_request.value == "on"
        elif isinstance(setting_request, BrowserScannerSettingsRequest):
            self.browser_scanner_enabled = setting_request.value == "on"
        else:
            logger.error(
                f"Canarydrops cannot apply a settings change for: {setting_request}"
            )
            return False
        queries.save_canarydrop(self)
        return True

    def get_url_components(
        self,
    ):
        return (
            queries.get_all_canary_path_elements(),
            queries.get_all_canary_pages(),
        )

    def generate_random_url(self, canary_domains: List[str]):
        """
        Return a URL generated at random with the saved Canarytoken.
        The random URL is also saved into the Canarydrop.
        """
        (path_elements, pages) = self.get_url_components()

        generated_url = random.choice(canary_domains) + "/"
        path = []
        for count in range(0, random.randint(1, 3)):
            if len(path_elements) == 0:
                break

            elem = path_elements[random.randint(0, len(path_elements) - 1)]
            path.append(elem)
            path_elements.remove(elem)
        path.append(self.canarytoken.value())

        path.append(pages[random.randint(0, len(pages) - 1)])
        generated_url += "/".join(path)
        # TODO: check how we want this caching to work. Use a property if needed.
        #       Or @lru.cache() or as it was but it's non-obvious
        # self.generated_url = generated_url
        # self.generated_url
        return generated_url

    def get_url(self, canary_domains: List[str]):
        return self.generate_random_url(canary_domains)

    def generate_random_hostname(self, with_random=False, nxdomain=False):
        """
        Return a hostname generated at random with the saved Canarytoken.
        The random hostname is also saved into the Canarydrop.
        """
        if nxdomain:
            domains = queries.get_all_canary_nxdomains()
        else:
            domains = queries.get_all_canary_domains()

        if with_random:
            generated_hostname = str(random.randint(1, 2**24)) + "."
        else:
            generated_hostname = ""

        generated_hostname += self.canarytoken.value() + "." + random.choice(domains)

        return generated_hostname

    def get_hostname(self, with_random=False, as_url=False, nxdomain=False):

        random_hostname = self.generate_random_hostname(
            with_random=with_random,
            nxdomain=nxdomain,
        )
        return ("http://" if as_url else "") + random_hostname

    def get_cloned_site_javascript(self):
        clonedsite_js = """
if (document.domain = "{CLONED_SITE_DOMAIN}" && document.domain != "www.{CLONED_SITE_DOMAIN}") {{
    var l = location.href;
    var r = document.referrer;
    var m = new Image();
    m.src = "{CANARYTOKEN_SITE}/"+
            "{CANARYTOKEN}.jpg?l="+
            encodeURI(l) + "&amp;r=" + encodeURI(r);
}}
            """.format(
            CLONED_SITE_DOMAIN=self.clonedsite,
            CANARYTOKEN_SITE=self.generated_hostname,
            CANARYTOKEN=self.canarytoken.value(),
        )
        return clonedsite_js

    @staticmethod
    def generate_mysql_usage(
        token: str, domain: str, port: int, encoded: bool = True
    ) -> str:
        magic_sauce = "SET @bb = CONCAT(\"CHANGE MASTER TO MASTER_PASSWORD='my-secret-pw', MASTER_RETRY_COUNT=1, "
        magic_sauce += f"MASTER_PORT={port}, "
        magic_sauce += f"MASTER_HOST='{domain}', "
        magic_sauce += f'MASTER_USER=\'{token}", @@lc_time_names, @@hostname, "\';");'
        if not encoded:
            usage = textwrap.dedent(
                f"""
                {magic_sauce}
                PREPARE stmt FROM @bb;
                EXECUTE stmt;
                START REPLICA;
                """
            )
        else:
            usage = textwrap.dedent(
                f"""
                SET @b = '{b64encode(magic_sauce.encode()).decode()}';
                SET @s2 = FROM_BASE64(@b);
                PREPARE stmt1 FROM @s2;
                EXECUTE stmt1;
                PREPARE stmt2 FROM @bb;
                EXECUTE stmt2;
                START REPLICA;
                """
            ).strip()
        return usage

    def get_kubeconfig(self):
        return self.kubeconfig

    def get_requested_output_channels(
        self,
    ):
        """Return a list containing the output channels configured in this
        Canarydrop."""
        channels: List[str] = []
        if self.alert_email_enabled and self.alert_email_recipient:
            channels.append(OUTPUT_CHANNEL_EMAIL)
        if self.alert_webhook_enabled and self.alert_webhook_url:
            channels.append(OUTPUT_CHANNEL_WEBHOOK)
        if self.alert_sms_enabled and self.alert_sms_recipient:
            channels.append(OUTPUT_CHANNEL_TWILIO_SMS)
        return channels

    def serialize(
        self,
    ):
        """
        Return a representation of this Canarydrop suitable for saving
        into redis.
        """
        serialized = json.loads(
            self.json(
                exclude={
                    "canarytoken",
                    "switchboard_settings",
                    "triggered_details",  # V2 compatible.
                }
            ),
        )  # TODO: check https://github.com/samuelcolvin/pydantic/issues/1409 and swap out when possible
        serialized["canarytoken"] = self.canarytoken.value()

        # V2 compatibility - timestamp and created_at are aliases on the
        # Canarydrop model. Redis just has timestamp.
        serialized["timestamp"] = serialized.pop("created_at")

        serialized["type"] = str(serialized["type"])
        for k, v in serialized.copy().items():
            if isinstance(v, bool):
                serialized[k] = str(v)
            if v is None:
                serialized.pop(k, None)
        if serialized["user"]:
            serialized["user"] = serialized["user"]["name"]

        if details := self.triggered_details.serialize_for_v2():
            serialized["triggered_list"] = json.dumps(details)
        # V2 stores `aws_output` as `output`
        if "aws_output" in serialized:
            serialized["output"] = serialized.pop("aws_output")
        # V2 stores `aws_region` as `region`
        if "aws_region" in serialized:
            serialized["region"] = serialized.pop("aws_region")
        return serialized

    def can_notify_again(self):
        # Design: need to rate limit the notifications.
        # Review where this is done.
        if len(self.triggered_details.hits) < 2:
            return True

        second_most_recent_hit, most_recent_hit = sorted(
            self.triggered_details.hits, key=lambda o: o.time_of_hit
        )[-2:]
        if (
            datetime.fromtimestamp(most_recent_hit.time_of_hit)
            - datetime.fromtimestamp(second_most_recent_hit.time_of_hit)
        ) < timedelta(seconds=1):
            return False
        else:
            return True

    def alertable(
        self,
    ):
        return queries.can_send_alert(canarydrop=self)  # and self.can_notify_again()

    def alerting(self) -> None:
        self.user.do_accounting(canarydrop=self)

    def get_csv_incident_list(self) -> str:
        csvOutput = io.StringIO()
        writer = csv.writer(csvOutput)

        if len(self.triggered_details.hits) > 0:  # pragma: no cover
            hit_class_dict = dict(self.triggered_details.hits[0])
            headers = [
                (i)
                for i in hit_class_dict.keys()
                if i not in ["token_type", "time_of_hit"]
            ]
            writer.writerow(["Timestamp"] + headers)
            for hit in self.triggered_details.hits:
                timestamp = hit.time_of_hit
                hit_id = datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S.%s"
                )
                hit_dict = dict(hit)
                data = [hit_id]
                for key in headers:
                    data.append(hit_dict.get(key, "N/A"))
                writer.writerow(data)
        else:
            writer.writerow("the token has not been triggered")

        return csvOutput.getvalue()

    def format_triggered_details_of_history_page(self) -> Dict[str, Any]:
        """
        Helper function as history.html still relies on v2 format.
        TODO: remove this when history.html is updated.
        Returns:
            Dict[str, Any]: v2 formatted incident list.
        """

        return self.triggered_details.serialize_for_v2(readable_time_format=True)
