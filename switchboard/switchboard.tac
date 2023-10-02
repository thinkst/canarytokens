import os
from pathlib import Path

import sentry_sdk
import sentry_sdk.utils

# import twisted
from sentry_sdk.integrations.redis import RedisIntegration
from twisted.application import internet, service
from twisted.logger import globalLogPublisher, Logger, LogLevel, textFileLogObserver
from twisted.names import dns
from twisted.python import logfile

from canarytokens.channel_dns import ChannelDNS, DNSServerFactory
from canarytokens.channel_http import ChannelHTTP
from canarytokens.channel_input_mtls import ChannelKubeConfig
from canarytokens.channel_input_mysql import ChannelMySQL
from canarytokens.channel_input_smtp import ChannelSMTP
from canarytokens.channel_input_wireguard import ChannelWireGuard
from canarytokens.channel_output_email import EmailOutputChannel
from canarytokens.channel_output_webhook import WebhookOutputChannel
from canarytokens.loghandlers import webhookLogObserver
from canarytokens.queries import (
    add_return_for_token,
    set_ip_info_api_key,
    update_tor_exit_nodes_loop,
)
from canarytokens.redismanager import DB
from canarytokens.settings import FrontendSettings, SwitchboardSettings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import set_template_env
from canarytokens.utils import get_deployed_commit_sha

# TODO: see if this is still needed.
# Removed for now
# from caa_monkeypatch import monkey_patch_caa_support
# monkey_patch_caa_support()

log = Logger()

switchboard_settings = SwitchboardSettings()
frontend_settings = FrontendSettings()

if switchboard_settings.IPINFO_API_KEY:
    set_ip_info_api_key(switchboard_settings.IPINFO_API_KEY.get_secret_value())


f = logfile.LogFile.fromFullPath(
    os.getenv("LOG_FILE", "switchboard.log"),
    rotateLength=switchboard_settings.SWITCHBOARD_LOG_SIZE,
    maxRotatedFiles=switchboard_settings.SWITCHBOARD_LOG_COUNT,
)
globalLogPublisher.addObserver(textFileLogObserver(f))

if os.getenv("ERROR_LOG_WEBHOOK", None):
    # Only create this log observer if the config is setup for it.
    log.info("Error log webhook enabled")
    globalLogPublisher.addObserver(webhookLogObserver())


def sentry_observer(event):
    # DESIGN: If sentry remains choice for Application Monitoring we can rework this.
    #         Note: Twisted logging and sentry appear to be slightly at odds.
    #         Secondly: Twisted observers should be non-blocking but that assumption has not been tested / measured.
    if (
        event.get("log_level") in [LogLevel.critical, LogLevel.error]
        and "log_failure" in event
    ):
        failure = event["log_failure"]
    elif event.get("isError") and "failure" in event:
        failure = event["failure"]
    else:
        return
    exc_type = failure.type
    exc_value = failure.value
    traceback = failure.getTracebackObject()
    sentry_sdk.capture_exception(error=(exc_type, exc_value, traceback))


if switchboard_settings.SENTRY_DSN and switchboard_settings.SENTRY_ENABLE:
    sentry_sdk.utils.MAX_STRING_LENGTH = 8192
    sentry_sdk.init(
        dsn=switchboard_settings.SENTRY_DSN,
        environment=switchboard_settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=0.2,
        integrations=[RedisIntegration()],
        release=get_deployed_commit_sha(),
    )
    globalLogPublisher.addObserver(sentry_observer)
    log.debug(f"Sentry enabled. Environment: {switchboard_settings.SENTRY_ENVIRONMENT}")

DB.set_db_details(switchboard_settings.REDIS_HOST, switchboard_settings.REDIS_PORT)
set_template_env(Path(switchboard_settings.TEMPLATES_PATH))
add_return_for_token(switchboard_settings.TOKEN_RETURN)


application = service.Application("Canarydrops Switchboard")

switchboard = Switchboard(switchboard_settings)

email_output_channel = EmailOutputChannel(
    switchboard=switchboard,
    frontend_settings=frontend_settings,
    switchboard_settings=switchboard_settings,
)
webhook_output_channel = WebhookOutputChannel(
    switchboard=switchboard,
    switchboard_scheme=switchboard_settings.SWITCHBOARD_SCHEME,
    frontend_domain=switchboard_settings.PUBLIC_DOMAIN,
)

dns_service = service.MultiService()

udp_factory = dns.DNSDatagramProtocol(
    DNSServerFactory(
        clients=[
            ChannelDNS(
                switchboard=switchboard,
                frontend_settings=frontend_settings,
                switchboard_scheme=switchboard_settings.SWITCHBOARD_SCHEME,
                switchboard_hostname=frontend_settings.DOMAINS[0],
            ),
        ],
    )
)

internet.UDPServer(switchboard_settings.CHANNEL_DNS_PORT, udp_factory, interface=switchboard_settings.CHANNEL_DNS_IP).setServiceParent(
    dns_service
)
dns_service.setServiceParent(application)

canarytokens_httpd = ChannelHTTP(
    frontend_settings=frontend_settings,
    switchboard_settings=switchboard_settings,
    switchboard=switchboard,
)
canarytokens_httpd.service.setServiceParent(application)

canarytokens_smtp = ChannelSMTP(
    frontend_settings=frontend_settings,
    switchboard_settings=switchboard_settings,
    switchboard=switchboard,
)
canarytokens_smtp.service.setServiceParent(application)

canarytokens_kubeconfig = ChannelKubeConfig(
    switchboard_settings=switchboard_settings,
    frontend_settings=frontend_settings,
    switchboard=switchboard,
)
canarytokens_kubeconfig.service.setServiceParent(application)

canarytokens_mysql = ChannelMySQL(
    port=switchboard_settings.CHANNEL_MYSQL_PORT,
    switchboard=switchboard,
    switchboard_scheme=switchboard_settings.SWITCHBOARD_SCHEME,
    switchboard_hostname=frontend_settings.DOMAINS[0],
)
canarytokens_mysql.service.setServiceParent(application)

canarytokens_wireguard = ChannelWireGuard(
    port=switchboard_settings.CHANNEL_WIREGUARD_PORT,
    switchboard=switchboard,
    switchboard_scheme=switchboard_settings.SWITCHBOARD_SCHEME,
    switchboard_hostname=frontend_settings.DOMAINS[0],
    switchboard_settings=switchboard_settings,
)
canarytokens_wireguard.service.setServiceParent(application)

# loop to update tor exit nodes every 30 min
loop_http = internet.task.LoopingCall(update_tor_exit_nodes_loop)
loop_http.start(1800)
