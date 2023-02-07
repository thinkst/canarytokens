""""
Base class for all canarydrop channels.
"""
from __future__ import annotations

import datetime
from typing import Any, Coroutine, List, Optional, Union

import twisted.internet.reactor
from twisted.internet import threads
from twisted.logger import Logger

from canarytokens import switchboard as sb
from canarytokens.canarydrop import Canarydrop

# from canarytokens.exceptions import DuplicateChannel
from canarytokens.models import (
    AnyTokenHit,
    GoogleChatAlertDetailsSectionData,
    GoogleChatCard,
    GoogleChatCardV2,
    GoogleChatHeader,
    GoogleChatPayload,
    GoogleChatSection,
    Memo,
    SlackAttachment,
    SlackField,
    TokenAlertDetailGeneric,
    TokenAlertDetails,
    TokenAlertDetailsSlack,
    TokenTypes,
)

log = Logger()


def format_as_slack_canaryalert(details: TokenAlertDetails) -> TokenAlertDetailsSlack:
    """
    Transforms `TokenAlertDetails` to `TokenAlertDetailsSlack`.
    """
    fields: List[SlackField] = [
        SlackField(title="Channel", value=details.channel),
        SlackField(title="Memo", value=details.memo),
        SlackField(
            title="time",
            value=details.time.strftime("%Y-%m-%d %H:%M:%S (UTC)"),
        ),
        SlackField(title="Manage", value=details.manage_url),
    ]

    attchments = [SlackAttachment(title_link=details.manage_url, fields=fields)]
    return TokenAlertDetailsSlack(
        # channel="#general",
        attachments=attchments,
    )


def format_as_googlechat_canaryalert(details: TokenAlertDetails) -> GoogleChatPayload:
    # construct google chat alert , top section
    top_section = GoogleChatSection(header="Alert Details")
    top_section.add_widgets(
        widgets_info=GoogleChatAlertDetailsSectionData(
            channel=details.channel,
            time=details.time.strftime("%Y-%m-%d %H:%M:%S (UTC)"),
            canarytoken=details.token,
            token_reminder=details.memo,
            manage_url=details.manage_url,
        ).get_googlechat_data()
    )
    # construct google chat alert , additional section
    additional_section = GoogleChatSection(header="Additional Details")
    additional_section.add_widgets(widgets_info=details.additional_data)

    # construct google chat alert card
    card = GoogleChatCard(
        header=GoogleChatHeader(
            title="Canarytoken Triggered",
            imageUrl="https://s3-eu-west-1.amazonaws.com/email-images.canary.tools/canary-logo-round.png",
            imageType="CIRCLE",
            imageAltText="Thinkst Canary",
        ),
        sections=[top_section, additional_section],
    )
    # make google chat payload
    return GoogleChatPayload(
        cardsV2=[GoogleChatCardV2(cardId="unique-card-id", card=card)]
    )


class Channel(object):
    CHANNEL = "Base"

    def __init__(
        self,
        switchboard: sb.Switchboard,
        backend_scheme: str,
        backend_hostname: str,
        name: Optional[str] = None,
    ):
        self.switchboard: sb.Switchboard = switchboard
        # DESIGN: What does Switchboard / channels need to know about back/frontend
        self.backend_scheme = backend_scheme
        self.backend_hostname = backend_hostname
        self.name = name or self.CHANNEL
        log.info("Started channel {name}".format(name=self.name))


class InputChannel(Channel):
    CHANNEL = "InputChannel"

    def __init__(
        self,
        switchboard: sb.Switchboard,
        backend_scheme: str,
        backend_hostname: str,
        name: str,
        unique_channel: bool = False,
    ) -> None:
        super(InputChannel, self).__init__(
            switchboard=switchboard,
            backend_scheme=backend_scheme,
            backend_hostname=backend_hostname,
            name=name,
        )
        self.register_input_channel(unique_channel)

    def register_input_channel(
        self,
        unique_channel: bool,
    ):
        if self.name in self.switchboard.input_channels and not unique_channel:
            self.switchboard.add_input_channel(name=self.name, channel=self)
        else:
            self.switchboard.add_input_channel(name=self.name, channel=self)

    @classmethod
    def gather_alert_details(
        cls,
        canarydrop: Canarydrop,
        protocol: str,
        host: str,  # DESIGN: Shift this to settings. Do we need to have this logic here?
    ) -> TokenAlertDetails:
        additional_data = (
            canarydrop.triggered_details.get_additional_data_for_notification()
        )
        return TokenAlertDetails(
            channel=cls.CHANNEL,
            token_type=canarydrop.type,
            src_ip=canarydrop.triggered_details.latest_hit().src_ip,
            time=datetime.datetime.utcnow(),
            memo=Memo(canarydrop.memo),
            token=canarydrop.canarytoken.value(),
            # TODO: this manage url should come from the backend / settings object.
            manage_url="{protocol}://{host}/manage?token={token}&auth={auth}".format(
                protocol=protocol,
                host=host,
                token=canarydrop.canarytoken.value(),
                auth=canarydrop.auth,
            ),
            additional_data=additional_data,  # TODO: additional details need to be re-worked.
        )

    @classmethod
    def format_email_canaryalert(
        cls,
        canarydrop: Canarydrop,
        protocol: str,
        host: str,  # DESIGN: Shift this to settings. Do we need to have this logic here?
    ) -> TokenAlertDetails:

        details = cls.gather_alert_details(
            canarydrop,
            protocol=protocol,
            host=host,
        )
        if canarydrop.type == TokenTypes.AWS_KEYS:
            # Override channel for alert readability.
            details.channel = "AWS API Key Token"
        return details

    #         msg = {}

    #         msg["time"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S (UTC)")
    #         msg["channel"] = self.name

    #         if "src_data" in kwargs and "aws_keys_event_source_ip" in kwargs["src_data"]:
    #             msg["src_ip"] = kwargs["src_data"]["aws_keys_event_source_ip"]
    #             msg["channel"] = "AWS API Key Token"

    #         if "src_data" in kwargs and "aws_keys_event_user_agent" in kwargs["src_data"]:
    #             msg["useragent"] = kwargs["src_data"]["aws_keys_event_user_agent"]

    #         if "src_data" in kwargs and "log4_shell_computer_name" in kwargs["src_data"]:
    #             msg["log4_shell_computer_name"] = kwargs["src_data"][
    #                 "log4_shell_computer_name"
    #             ]

    #         if params.get("body_length", 999999999) <= 140:
    #             msg["body"] = """Canarydrop@{time} via {channel_name}: """.format(
    #                 channel_name=self.name, time=msg["time"]
    #             )
    #             capacity = 140 - len(msg["body"])
    #             msg["body"] += canarydrop.memo[:capacity]
    #         else:
    #             msg[
    #                 "body"
    #             ] = """
    # One of your canarydrops was triggered.
    # Channel: {channel_name}
    # Time   : {time}
    # Memo   : {memo}
    # {additional_data}
    # Manage your settings for this Canarydrop:
    # {protocol}://{host}/manage?token={token}&auth={auth}""".format(
    #                 channel_name=self.name,
    #                 time=msg["time"],
    #                 memo=canarydrop.memo,
    #                 additional_data=self.format_additional_data(**kwargs),
    #                 protocol=protocol,
    #                 host=host,
    #                 token=canarydrop["canarytoken"],
    #                 auth=canarydrop["auth"],
    #             )
    #             msg[
    #                 "manage"
    #             ] = "{protocol}://{host}/manage?token={token}&auth={auth}".format(
    #                 protocol=protocol,
    #                 host=host,
    #                 token=canarydrop["canarytoken"],
    #                 auth=canarydrop["auth"],
    #             )
    #             msg[
    #                 "history"
    #             ] = "{protocol}://{host}/history?token={token}&auth={auth}".format(
    #                 protocol=protocol,
    #                 host=host,
    #                 token=canarydrop["canarytoken"],
    #                 auth=canarydrop["auth"],
    #             )

    #         if params.get("subject_required", False):
    #             msg["subject"] = settings.ALERT_EMAIL_SUBJECT
    #         if params.get("from_display_required", False):
    #             msg["from_display"] = settings.ALERT_EMAIL_FROM_DISPLAY
    #         if params.get("from_address_required", False):
    #             msg["from_address"] = settings.ALERT_EMAIL_FROM_ADDRESS
    #         return msg

    @classmethod
    def format_webhook_canaryalert(
        cls,
        canarydrop: Canarydrop,
        protocol: str,
        host: str,  # DESIGN: Shift this to settings. Do we need to have this logic here?
    ) -> Union[TokenAlertDetailsSlack, TokenAlertDetailGeneric]:
        # TODO: Need to add `host` and `protocol` that can be used to manage the token.
        googlechat_hook_base_url = "https://chat.googleapis.com"
        details = cls.gather_alert_details(
            canarydrop,
            protocol=protocol,
            host=host,
        )
        if canarydrop.alert_webhook_url and (
            "https://hooks.slack.com" in canarydrop.alert_webhook_url
        ):
            return format_as_slack_canaryalert(details=details)
        elif canarydrop.alert_webhook_url and (
            str(canarydrop.alert_webhook_url).startswith(googlechat_hook_base_url)
        ):
            return format_as_googlechat_canaryalert(details=details)
        else:
            return TokenAlertDetailGeneric(**details.dict())

    def dispatch(self, *, canarydrop: Canarydrop, token_hit: AnyTokenHit) -> None:
        """
        Spins off a `switchboard.dispatch` which notifies on all neccessary channels.
        """
        log.info(f"reactor is running?: {twisted.internet.reactor.running}")
        d = threads.deferToThread(
            self.switchboard.dispatch,
            canarydrop=canarydrop,
            token_hit=token_hit,
        )
        d.addCallback(self.dispatch_success)
        d.addErrback(self.dispatch_errored)

    def dispatch_success(self, info: str):
        log.info(f"Dispatched alert: {info}")

    def dispatch_errored(self, info: str):
        log.error(f"Dispatch errored: {info}")


class OutputChannel(Channel):
    CHANNEL = "OutputChannel"

    def __init__(
        self,
        switchboard: sb.Switchboard,
        backend_scheme: str,
        backend_hostname: str,
        name: Optional[str] = None,
    ):
        super(OutputChannel, self).__init__(
            switchboard=switchboard,
            backend_scheme=backend_scheme,
            backend_hostname=backend_hostname,
            name=name,
        )
        self.register_output_channel()

    def register_output_channel(
        self,
    ):
        self.switchboard.add_output_channel(name=self.name, channel=self)

    def send_alert(
        self,
        input_channel: InputChannel,
        canarydrop: Canarydrop,
        token_hit: AnyTokenHit,
    ) -> None:

        self.do_send_alert(
            input_channel=input_channel,
            canarydrop=canarydrop,
            token_hit=token_hit,
        )

    def do_send_alert(
        self,
        input_channel: InputChannel,
        canarydrop: Canarydrop,
        token_hit: AnyTokenHit,
    ) -> Coroutine[Any, Any, None]:
        #  Design: Make this a typing.protocol and drop this.
        raise NotImplementedError("Generic Output channel cannot `do_send_alert`")
