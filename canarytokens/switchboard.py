"""
Class that receives alerts, and dispatches them to the registered endpoint.
"""
from __future__ import annotations

from typing import Dict

from twisted.logger import Logger

from canarytokens import channel, queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.exceptions import DuplicateChannel, InvalidChannel
from canarytokens.models import AnyTokenHit

log = Logger()


class Switchboard:
    # DESIGN: Do we need this to be a class?
    def __init__(
        self,
    ):
        """Return a new Switchboard instance."""
        self.input_channels = {}
        self.output_channels: Dict[str, channel.OutputChannel] = {}
        log.info("Canarytokens switchboard started")

    def add_input_channel(self, name=None, channel=None):
        """Register a new input channel with the switchboard.

        Arguments:
        name -- unique name for the input channel
        formatters -- a dict in the form { TYPE: METHOD,...} used to lookup
                      the channel's format method depending on the alert type
        """
        self.input_channels[name] = channel

    def add_output_channel(self, name=None, channel=None):
        """Register a new output channel with the switchboard.

        Arguments:
        name -- unique name for the input channel
        formatters -- a dict in the form { TYPE: METHOD,...} used to lookup
                      the channel's format method depending on the alert type
        """
        if name in self.output_channels:
            raise DuplicateChannel()

        self.output_channels[name] = channel

    def dispatch(self, canarydrop: Canarydrop, token_hit: AnyTokenHit) -> str:
        """
        Calls the correct alerting method for the trigger and channel combination.
        """
        if token_hit.input_channel not in self.input_channels:
            raise InvalidChannel(
                f"{token_hit.input_channel} not in input channels: {self.input_channels}"
            )

        if not canarydrop.alertable():
            log.warn(
                "Token {token} is not alertable at this stage.".format(
                    token=canarydrop.canarytoken.value(),
                ),
            )
            return

        # TODO: update accounting info
        queries.do_accounting(canarydrop=canarydrop, alert_expiry=60)
        for requested_output_channel in canarydrop.get_requested_output_channels():
            output_channel = self.output_channels.get(requested_output_channel, None)
            if output_channel is None:
                log.error(
                    f"Output channel: {requested_output_channel} is not available. Dropping the notification for: {canarydrop.canarytoken.value()} on this channel."
                )
                continue
            # TODO: we can fire all these off in 'parallel'
            output_channel.send_alert(
                input_channel=self.input_channels[token_hit.input_channel],
                canarydrop=canarydrop,
                token_hit=token_hit,
            )
        return f"Dispatched to output channel for: {canarydrop.canarytoken.value()}"
