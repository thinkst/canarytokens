from datetime import datetime
from typing import Optional

from twisted.application import internet
from twisted.logger import Logger

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import InputChannel
from canarytokens.constants import INPUT_CHANNEL_POSTGRESQL
from canarytokens.exceptions import NoCanarydropFound
from canarytokens.models import PostgreSQLAdditionalInfo, PostgreSQLTokenHit, TokenTypes
from canarytokens.postgresql import PostgreSQLFactory, compute_md5_response
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

log = Logger()


class ChannelPostgreSQL(InputChannel):
    CHANNEL = INPUT_CHANNEL_POSTGRESQL

    def __init__(
        self,
        port: int,
        switchboard: Switchboard,
        switchboard_scheme: str,
        switchboard_hostname: str,
    ) -> None:
        InputChannel.__init__(
            self,
            switchboard=switchboard,
            switchboard_scheme=switchboard_scheme,
            switchboard_hostname=switchboard_hostname,
            name=self.CHANNEL,
            unique_channel=True,
        )
        self.service = internet.TCPServer(
            port,
            PostgreSQLFactory(channel=self),
        )

    def handle_auth(
        self,
        protocol,
        username,
        database,
        client_hash,
        salt,
        src_ip,
        client_params=None,
    ):
        all_mappings = queries.postgresql_passwordmap_getall()
        if not all_mappings:
            protocol.deny()
            return

        # Find which stored inner_hash produces the client's response with this salt
        matched_token = None
        for inner_hash, token_value in all_mappings.items():
            if client_hash == compute_md5_response(inner_hash, salt):
                matched_token = token_value
                break

        if not matched_token:
            protocol.deny()
            return

        canarytoken = Canarytoken(value=matched_token)
        try:
            canarydrop: Optional[Canarydrop] = queries.get_canarydrop(canarytoken)
        except NoCanarydropFound:
            queries.postgresql_passwordmap_del(inner_hash)
            protocol.deny()
            return

        geo_info = queries.get_geoinfo(ip=src_ip)
        is_tor_relay = queries.is_tor_relay(src_ip)

        log_data = {"Database": [database]}
        if client_params:
            for key, value in client_params.items():
                log_data[key] = [value]

        token_hit = PostgreSQLTokenHit(
            token_type=TokenTypes.POSTGRESQL,
            time_of_hit=datetime.utcnow().strftime("%s.%f"),
            src_ip=src_ip,
            input_channel=INPUT_CHANNEL_POSTGRESQL,
            geo_info=geo_info,
            is_tor_relay=is_tor_relay,
            postgresql_username=username,
            additional_info=PostgreSQLAdditionalInfo(
                postgresql_log_data=log_data,
            ),
        )

        canarydrop.add_canarydrop_hit(token_hit=token_hit)
        self.dispatch(canarydrop=canarydrop, token_hit=token_hit)
        protocol.deny()
