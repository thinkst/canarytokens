from __future__ import annotations

from typing import Dict, Optional, Tuple

from twisted.internet import defer
from twisted.logger import Logger
from twisted.names import dns, error, server
from twisted.names.dns import Name, Query

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import InputChannel
from canarytokens.constants import INPUT_CHANNEL_DNS
from canarytokens.exceptions import NoCanarytokenFound, NoCanarydropFound
from canarytokens.models import TokenTypes
from canarytokens.settings import FrontendSettings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken

# TODO: logging is still very much WIP.
log = Logger()


def handle_query_name(query_name: Name) -> Tuple[Canarydrop, Dict[str, str]]:
    """ """
    query_name_decoded: str = query_name.name.decode()

    token = Canarytoken(value=query_name_decoded)

    canarydrop = queries.get_canarydrop(canarytoken=token)
    # DESIGN: If lookups are unique per type we should use that for this lookup.
    #         V2
    src_data = Canarytoken.look_for_source_data(query_name=query_name_decoded)
    log.info(
        f"Recovered: {repr([o for o in src_data.items()])} for {query_name_decoded}"
    )
    return canarydrop, src_data


class DNSServerFactory(server.DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        if message.answer:
            return
        query = message.queries[0]
        if address:
            src_ip = address[0]
            if address[1] == 0:
                log.debug(
                    ("Dropping request from {src} because source port is 0").format(
                        src=src_ip,
                    ),
                )
                return None
        else:
            src_ip = protocol.transport.socket.getpeername()[0]

        return (
            self.resolver.query(query, src_ip)
            .addCallback(self.gotResolverResponse, protocol, message, address)
            .addErrback(self.gotResolverError, protocol, message, address)
        )

    def gotResolverError(self, failure, protocol, message, address):
        if failure.check(error.DNSQueryRefusedError):
            response = self._responseFromMessage(message=message, rCode=dns.EREFUSED)

            self.sendReply(protocol, response, address)
            self._verboseLog("Lookup failed")
        else:
            super(DNSServerFactory, self).gotResolverError(
                failure,
                protocol,
                message,
                address,
            )


class ChannelDNS(InputChannel):
    CHANNEL = INPUT_CHANNEL_DNS

    def __init__(
        self,
        # listen_domain: str,
        switchboard: Switchboard,
        switchboard_scheme: str,
        switchboard_hostname: str,
        frontend_settings: FrontendSettings,
        # **kwargs,
    ):
        super(ChannelDNS, self).__init__(
            switchboard=switchboard,
            switchboard_scheme=switchboard_scheme,
            switchboard_hostname=switchboard_hostname,
            name=self.CHANNEL,
        )
        self.frontend_settings: FrontendSettings = frontend_settings

        # self.listen_domain = listen_domain

        # TODO: This should be passed in an not grabbed from redis
        self.canary_domains = self.frontend_settings.DOMAINS

    def _do_ns_response(self, name=None):
        """
        Calculate the response to a query.
        """
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_NS(
                ttl=300,
                name=".".join(["ns1", name.decode()]),
            ),
            type=dns.NS,
            auth=True,
            ttl=300,
        )
        additional = dns.RRHeader(
            name=".".join(["ns1", name.decode()]),
            payload=dns.Record_A(ttl=10, address=self.frontend_settings.PUBLIC_IP),
            type=dns.A,
            auth=True,
            ttl=300,
        )
        answers = [answer]
        authority: list[str] = []
        additional = [additional]
        return answers, authority, additional

    def _do_soa_response(self, name=None):
        """
        Ensure a standard response to a SOA query.
        """
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_SOA(
                mname=name.lower(),
                rname=".".join(["info", name.lower().decode()]),
                serial=0,
                refresh=300,
                retry=300,
                expire=300,
                minimum=300,
                ttl=300,
            ),
            type=dns.SOA,
            auth=True,
            ttl=300,
        )
        answers = [answer]
        authority = []
        additional = []

        return answers, authority, additional

    def _do_dynamic_response(self, name=None):
        """
        Calculate the response to a query.
        """
        log.info(f"Building A record: ip = {self.frontend_settings.PUBLIC_IP}")
        ttl = 10

        if name.lower().decode() in self.canary_domains:
            # This is a resolution of the apex domain, not a token, so we can bump up the TTL
            ttl = 600  # 10 min seems plenty short enough to allow for IP changes without getting overloaded

        payload = dns.Record_A(ttl=ttl, address=self.frontend_settings.PUBLIC_IP)
        answer = dns.RRHeader(
            name=name, payload=payload, type=dns.A, auth=True, ttl=ttl
        )
        answers = [answer]
        authority: list[str] = []
        additional: list[str] = []
        return answers, authority, additional

    def _do_no_response(
        self, query: Optional[Query] = None
    ) -> tuple[list[str], list[str], list[str]]:
        """
        Calculate the response to a query.
        """
        answers: list[str] = []
        authority: list[str] = []
        additional: list[str] = []
        return answers, authority, additional

    def query(self, query: Query, src_ip: str):  # noqa C901
        """
        Check if the query should be answered dynamically, otherwise dispatch to
        the fallback resolver.
        """
        try:
            log.info("Query: {} sent {}".format(src_ip, query))
        except UnicodeDecodeError:
            log.info(f"Non-ascii query received: {query.name.name}")
            return defer.fail(error.DomainError())

        IS_NX_DOMAIN = any(
            [
                query.name.name.lower().decode().endswith(f".{d}")
                for d in self.frontend_settings.NXDOMAINS
            ],
        )

        IS_DOMAIN = any(
            [query.name.name.lower().decode().endswith(d) for d in self.canary_domains]
        )
        if not IS_DOMAIN and not IS_NX_DOMAIN:
            return defer.fail(error.DNSQueryRefusedError())

        if query.type == dns.NS:
            return defer.succeed(self._do_ns_response(name=query.name.name))

        if query.type == dns.SOA:
            return defer.succeed(self._do_soa_response(name=query.name.name))

        if query.type != dns.A:
            return defer.succeed(self._do_no_response(query=query))
        log.info(f"handling query:  {query.name}")
        try:
            canarydrop, src_data = handle_query_name(query_name=query.name)
        except NoCanarytokenFound:
            log.info(f"Query: {query.name} does not match a token.")
            return defer.succeed(self._do_dynamic_response(name=query.name.name))
        except NoCanarydropFound as e:
            log.info(f"Query: {query.name} Error: {e}")
            return defer.succeed(self._do_dynamic_response(name=query.name.name))
        except Exception as e:
            log.error(f"Query: {query.name} failed to handle. Error: {e}")
            return defer.succeed(self._do_dynamic_response(name=query.name.name))
        # TODO: What was the deal with this my_sql special case!
        # Ignoring for now but needs a look see.
        # if canarydrop._drop['type'] == 'my_sql':
        #     d = deferLater(...)
        if (
            canarydrop.type
            in [TokenTypes.LOG4SHELL, TokenTypes.WINDOWS_DIR, TokenTypes.CMD]
            and src_data == {}
        ):
            return defer.succeed(self._do_dynamic_response(name=query.name.name))

        token_hit = Canarytoken.create_token_hit(
            token_type=canarydrop.type,
            input_channel=self.CHANNEL,
            src_ip=src_ip,
            hit_info=src_data,
        )
        # DESIGN: add all details to redis here.
        try:
            canarydrop.add_canarydrop_hit(token_hit=token_hit)
        except Exception as e:
            log.error(
                f"Failed to add hit to token {canarydrop.canarytoken.value()}: {token_hit}"
            )
            raise e

        self.dispatch(canarydrop=canarydrop, token_hit=token_hit)

        if IS_NX_DOMAIN:  # pragma: no cover
            if canarydrop.type not in [TokenTypes.ADOBE_PDF, TokenTypes.SIGNED_EXE]:
                log.info(
                    "Token {token} hit the NX domain and is not a pdf. TokenType: {token_type}",
                    token=canarydrop.canarytoken.value(),
                    token_type=canarydrop.type,
                )
            return defer.fail(error.DomainError())
        return defer.succeed(self._do_dynamic_response(name=query.name.name))

    def lookupCAA(self, name, timeout):  # pragma: no cover
        """Respond with NXdomain to a -t CAA lookup."""
        return defer.fail(error.DomainError())

    def lookupAllRecords(self, name, timeout):  # pragma: no cover
        """Respond with error to a -t ANY lookup."""
        return defer.fail(error.DomainError())

    # def format_additional_data(self, **kwargs):
    #     log.info(str(kwargs))
    #     additional_report = "Source IP : {ip}".format(ip=kwargs["src_ip"])

    #     if "src_data" in kwargs:

    #         if "sql_username" in kwargs["src_data"]:
    #             additional_report += "\nSQL Server User: {username}".format(
    #                 username=kwargs["src_data"]["sql_username"],
    #             )

    #         if "mysql_username" in kwargs["src_data"]:
    #             additional_report += "\nMySQL User: {username}".format(
    #                 username=kwargs["src_data"]["mysql_username"],
    #             )

    #         if "linux_inotify_filename_access" in kwargs["src_data"]:
    #             additional_report += "\nLinux File Access: {filename}".format(
    #                 filename=kwargs["src_data"]["linux_inotify_filename_access"],
    #             )

    #         if "generic_data" in kwargs["src_data"]:
    #             additional_report += "\nGeneric data: {generic_data}".format(
    #                 generic_data=kwargs["src_data"]["generic_data"],
    #             )

    #         if "dtrace_uid" in kwargs["src_data"]:
    #             additional_report += "\nDTrace UID: {uid}".format(
    #                 uid=kwargs["src_data"]["dtrace_uid"],
    #             )

    #         if "dtrace_hostname" in kwargs["src_data"]:
    #             additional_report += "\nDTrace hostname: {hostname}".format(
    #                 hostname=kwargs["src_data"]["dtrace_hostname"],
    #             )

    #         if "dtrace_command" in kwargs["src_data"]:
    #             additional_report += "\nDTrace command: {command}".format(
    #                 command=kwargs["src_data"]["dtrace_command"],
    #             )

    #         if "dtrace_filename" in kwargs["src_data"]:
    #             additional_report += "\nDTrace filename: {filename}".format(
    #                 filename=kwargs["src_data"]["dtrace_filename"],
    #             )

    #         if (
    #             "windows_desktopini_access_username" in kwargs["src_data"]
    #             and "windows_desktopini_access_domain" in kwargs["src_data"]
    #         ):
    #             if "windows_desktopini_access_hostname" in kwargs["src_data"]:
    #                 additional_report += "\nWindows Directory Browsing By: {domain}\{username} from {hostname}".format(
    #                     username=kwargs["src_data"][
    #                         "windows_desktopini_access_username"
    #                     ],
    #                     domain=kwargs["src_data"]["windows_desktopini_access_domain"],
    #                     hostname=kwargs["src_data"][
    #                         "windows_desktopini_access_hostname"
    #                     ],
    #                 )
    #             else:
    #                 additional_report += (
    #                     "\nWindows Directory Browsing By: {domain}\{username}".format(
    #                         username=kwargs["src_data"][
    #                             "windows_desktopini_access_username"
    #                         ],
    #                         domain=kwargs["src_data"][
    #                             "windows_desktopini_access_domain"
    #                         ],
    #                     )
    #                 )

    #         if "aws_keys_event_source_ip" in kwargs["src_data"]:
    #             additional_report += "\nAWS Keys used by: {ip}".format(
    #                 ip=kwargs["src_data"]["aws_keys_event_source_ip"],
    #             )

    #         if "log4_shell_computer_name" in kwargs["src_data"]:
    #             additional_report += (
    #                 "\nComputer name from Log4J shell: {computer_name}".format(
    #                     computer_name=kwargs["src_data"]["log4_shell_computer_name"],
    #                 )
    #             )

    #     return additional_report

    def _handleMySqlErr(self, result):  # pragma: no cover
        log.error(f"Error dispatching MySQL alert: {result}")
