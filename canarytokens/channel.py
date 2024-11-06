""""
Base class for all canarydrop channels.
"""

from __future__ import annotations

import datetime
from typing import Any, Coroutine, Optional, Union

import twisted.internet.reactor
from twisted.internet import threads
from twisted.logger import Logger

from canarytokens import switchboard as sb
from canarytokens.canarydrop import Canarydrop

# from canarytokens.exceptions import DuplicateChannel
from canarytokens.models import (
    AnyTokenHit,
    AnyTokenExposedHit,
    Memo,
    MsTeamsTitleSection,
    MsTeamsDetailsSection,
    MsTeamsPotentialAction,
    TokenAlertDetails,
    TokenAlertDetailsMsTeams,
)

log = Logger()



def format_as_ms_teams_canaryalert(
    details: TokenAlertDetails,
) -> TokenAlertDetailsMsTeams:
    sections = [
        MsTeamsTitleSection(activityTitle="<b>Canarytoken triggered</b>"),
        MsTeamsDetailsSection(
            canarytoken=details.token,
            token_reminder=details.memo,
            src_data=details.src_data if details.src_data else None,
            additional_data=details.additional_data,
        ),
    ]

    return TokenAlertDetailsMsTeams(
        summary="Canarytoken triggered",
        sections=sections,
        potentialAction=[
            MsTeamsPotentialAction(name="Manage", target=[details.manage_url])
        ],
    )


class Channel(object):
    CHANNEL = "Base"

    def __init__(
        self,
        switchboard: sb.Switchboard,
        switchboard_scheme: str,
        hostname: str,
        name: Optional[str] = None,
    ):
        self.switchboard: sb.Switchboard = switchboard
        # DESIGN: What does Switchboard / channels need to know about back/frontend
        self.switchboard_scheme = switchboard_scheme
        self.hostname = hostname
        self.name = name or self.CHANNEL
        log.info("Started channel {name}".format(name=self.name))


class InputChannel(Channel):
    CHANNEL = "InputChannel"

    def __init__(
        self,
        switchboard: sb.Switchboard,
        switchboard_scheme: str,
        switchboard_hostname: str,
        name: str,
        unique_channel: bool = False,
    ) -> None:
        super(InputChannel, self).__init__(
            switchboard=switchboard,
            switchboard_scheme=switchboard_scheme,
            hostname=switchboard_hostname,
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
        hit = canarydrop.triggered_details.latest_hit()
        additional_data = hit.get_additional_data_for_notification()
        if canarydrop.cmd_process:
            additional_data["cmd_process"] = canarydrop.cmd_process

        return TokenAlertDetails(
            channel=cls.CHANNEL,
            token_type=canarydrop.type,
            src_ip=hit.src_ip,
            time=datetime.datetime.utcnow(),
            memo=Memo(canarydrop.memo),
            token=canarydrop.canarytoken.value(),
            # TODO: this manage url should come from the frontend / settings object.
            manage_url=canarydrop.build_manage_url(protocol, host),
            additional_data=additional_data,  # TODO: additional details need to be re-worked.
            public_domain=host,
        )

    def dispatch(
        self,
        *,
        canarydrop: Canarydrop,
        token_hit: Union[AnyTokenHit, AnyTokenExposedHit],
    ) -> None:
        """
        Spins off a `switchboard.dispatch` which notifies on all necessary channels.
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
        switchboard_scheme: str,
        frontend_domain: str,
        name: Optional[str] = None,
    ):
        super(OutputChannel, self).__init__(
            switchboard=switchboard,
            switchboard_scheme=switchboard_scheme,
            hostname=frontend_domain,
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
        token_hit: Union[AnyTokenHit, AnyTokenExposedHit],
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
        token_hit: Union[AnyTokenHit, AnyTokenExposedHit],
    ) -> Coroutine[Any, Any, None]:
        #  Design: Make this a typing.protocol and drop this.
        raise NotImplementedError("Generic Output channel cannot `do_send_alert`")
