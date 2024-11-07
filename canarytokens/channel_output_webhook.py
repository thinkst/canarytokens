"""
Output channel that sends to webhooks.
"""

from typing import Dict, Union

import advocate
import requests
from pydantic import HttpUrl
from twisted.logger import Logger

from canarytokens import canarydrop
from canarytokens.channel import InputChannel, OutputChannel
from canarytokens.constants import OUTPUT_CHANNEL_WEBHOOK
from canarytokens.models import (
    AnyTokenHit,
    AnyTokenExposedHit,
    Memo,
    TokenExposedDetails,
    TokenExposedHit,
)
from canarytokens.webhook_formatting import format_details_for_webhook, get_webhook_type

log = Logger()


class WebhookOutputChannel(OutputChannel):
    CHANNEL = OUTPUT_CHANNEL_WEBHOOK

    def do_send_alert(
        self,
        input_channel: InputChannel,
        canarydrop: canarydrop.Canarydrop,
        token_hit: Union[AnyTokenHit, AnyTokenExposedHit],
    ) -> None:
        # TODO we should format using the hit directly,
        #      we use the drop to get the latest when we already have it
        url = canarydrop.alert_webhook_url
        if not (url.startswith("http://") or url.startswith("https://")):
            log.error(
                f"alert_webhook_url must start with http[s]://; url found for drop {canarydrop.canarytoken.value()}: {url}"
            )

        if isinstance(token_hit, TokenExposedHit):
            details = TokenExposedDetails(
                token_type=token_hit.token_type,
                token=canarydrop.canarytoken.value(),
                key_id=canarydrop.aws_access_key_id,
                memo=Memo(canarydrop.memo),
                public_location=token_hit.public_location,
                exposed_time=token_hit.time_of_hit,
                manage_url=canarydrop.build_manage_url(
                    self.switchboard_scheme, self.hostname
                ),
                public_domain=self.hostname,
            )
        else:
            details = input_channel.gather_alert_details(
                canarydrop=canarydrop,
                protocol=self.switchboard_scheme,
                host=self.hostname,
            )

        webhook_type = get_webhook_type(url)
        payload = format_details_for_webhook(webhook_type, details)

        success = self.generic_webhook_send(
            payload=payload.json_safe_dict(),
            alert_webhook_url=canarydrop.alert_webhook_url,
        )
        if success:
            canarydrop.clear_alert_failures()
        else:
            canarydrop.record_alert_failure()
            if (
                canarydrop.alert_failure_count
                > self.switchboard.switchboard_settings.MAX_ALERT_FAILURES
            ):
                log.info(
                    f"Webhook for token {canarydrop.canarytoken.value()} has returned too many errors, disabling it."
                )
                canarydrop.disable_alert_webhook()
                canarydrop.clear_alert_failures()

    def generic_webhook_send(
        self,
        payload: Dict[str, str],
        alert_webhook_url: HttpUrl,
    ) -> bool:
        # Design: wrap in a retry?
        try:
            validator = advocate.AddrValidator(port_whitelist=set(range(0, 65535)))
            response = advocate.post(
                url=str(alert_webhook_url),
                json=payload,
                timeout=(2, 2),
                validator=validator,
            )
            response.raise_for_status()
            log.info(f"Successfully sent to {alert_webhook_url}")
            return True
        except advocate.HTTPError:
            log.debug(
                f"Failed sending request to webhook {alert_webhook_url}.",
            )
        except advocate.exceptions.UnacceptableAddressException:
            log.debug(
                f"Disallowed requests to {alert_webhook_url}.",
            )
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            log.debug(
                f"Failed connecting to webhook {alert_webhook_url}.",
            )
        return False
