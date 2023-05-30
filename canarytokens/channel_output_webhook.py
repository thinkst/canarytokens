"""
Output channel that sends to webhooks.
"""
from typing import Dict

import requests
from pydantic import HttpUrl
from twisted.logger import Logger

from canarytokens import canarydrop
from canarytokens.channel import InputChannel, OutputChannel
from canarytokens.constants import OUTPUT_CHANNEL_WEBHOOK
from canarytokens.models import AnyTokenHit

log = Logger()


class WebhookOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_WEBHOOK

    def do_send_alert(
        self,
        input_channel: InputChannel,
        canarydrop: canarydrop.Canarydrop,
        token_hit: AnyTokenHit,
    ) -> None:
        payload = input_channel.format_webhook_canaryalert(
            canarydrop=canarydrop,
            host=self.hostname,
            protocol=self.switchboard_scheme,
        )

        self.generic_webhook_send(
            payload=payload.json_safe_dict(),
            alert_webhook_url=canarydrop.alert_webhook_url,
        )

    def generic_webhook_send(
        self,
        payload: Dict[str, str],
        alert_webhook_url: HttpUrl,
    ) -> None:
        # Design: wrap in a retry?
        try:
            response = requests.post(
                url=str(alert_webhook_url), json=payload, timeout=(3, 10)
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            log.error(
                f"Failed sending request to webhook {alert_webhook_url}.",
            )
        except requests.exceptions.ConnectionError:
            log.error(
                f"Failed connecting to webhook {alert_webhook_url}.",
            )
        else:
            log.info(f"Successfully sent to {alert_webhook_url}")
