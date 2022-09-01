import os
from pathlib import Path

import sentry_sdk
import sentry_sdk.utils
import twisted
import twisted.logger
from sentry_sdk.integrations.redis import RedisIntegration
from twisted.application import internet, service
from twisted.logger import globalLogPublisher
from twisted.names import dns

from canarytokens.channel_dns import ChannelDNS, DNSServerFactory
from canarytokens.channel_http import ChannelHTTP
from canarytokens.channel_input_mtls import ChannelKubeConfig
from canarytokens.channel_input_mysql import ChannelMySQL
from canarytokens.channel_input_smtp import ChannelSMTP
from canarytokens.channel_input_wireguard import ChannelWireGuard
from canarytokens.channel_output_email import EmailOutputChannel
from canarytokens.channel_output_webhook import WebhookOutputChannel
from canarytokens.queries import add_return_for_token, update_tor_exit_nodes_loop
from canarytokens.redismanager import DB
from canarytokens.settings import BackendSettings, Settings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import set_template_env
from canarytokens.utils import get_deployed_commit_sha

# TODO: see if this is still needed.
# Removed for now
# from caa_monkeypatch import monkey_patch_caa_support
# monkey_patch_caa_support()

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
switchboard_settings = Settings(_env_file=dir_path / "switchboard.env")
backend_settings = BackendSettings(_env_file=switchboard_settings.BACKEND_SETTINGS_PATH)

sentry_sdk.utils.MAX_STRING_LENGTH = 8192
sentry_sdk.init(
    dsn=switchboard_settings.SENTRY_DSN,
    environment=switchboard_settings.SENTRY_ENVIRONMENT,
    traces_sample_rate=0.2,
    integrations=[RedisIntegration()],
    release=get_deployed_commit_sha(),
)


def sentry_observer(event):
    # DESIGN: If sentry remains choice for Application Monitoring we can rework this.
    #         Note: Twisted logging and sentry appear to be slightly at odds.
    #         Secondly: Twisted observers should be non-blocking but that assumption has not been tested / measured.
    if (
        event.get("log_level") == twisted.logger.LogLevel.critical
        and "log_failure" in event
    ):
        failure = event["log_failure"]
        exc_type = failure.type
        exc_value = failure.value
        traceback = failure.getTracebackObject()
        sentry_sdk.capture_exception(error=(exc_type, exc_value, traceback))

    elif event.get("isError") and "failure" in event:
        failure = event["failure"]
        exc_type = failure.type
        exc_value = failure.value
        traceback = failure.getTracebackObject()
        sentry_sdk.capture_exception(error=(exc_type, exc_value, traceback))


globalLogPublisher.addObserver(sentry_observer)

DB.set_db_details(switchboard_settings.REDIS_HOST, switchboard_settings.REDIS_PORT)
set_template_env(Path(switchboard_settings.TEMPLATES_PATH))
add_return_for_token(switchboard_settings.TOKEN_RETURN)


application = service.Application("Canarydrops Switchboard")

switchboard = Switchboard()

email_output_channel = EmailOutputChannel(
    switchboard=switchboard,
    backend_settings=backend_settings,
    settings=switchboard_settings,
)
webhook_output_channel = WebhookOutputChannel(
    switchboard=switchboard,
    backend_scheme=backend_settings.BACKEND_SCHEME,
    backend_hostname=backend_settings.BACKEND_HOSTNAME,
)

dns_service = service.MultiService()

factory = DNSServerFactory(
    clients=[
        ChannelDNS(
            listen_domain=switchboard_settings.LISTEN_DOMAIN,
            switchboard=switchboard,
            settings=switchboard_settings,
            backend_scheme=backend_settings.BACKEND_SCHEME,
            backend_hostname=backend_settings.BACKEND_HOSTNAME,
        ),
    ],
)
udp_factory = dns.DNSDatagramProtocol(factory)
internet.TCPServer(switchboard_settings.CHANNEL_DNS_PORT, factory).setServiceParent(
    dns_service
)
internet.UDPServer(switchboard_settings.CHANNEL_DNS_PORT, udp_factory).setServiceParent(
    dns_service
)
dns_service.setServiceParent(application)

canarytokens_httpd = ChannelHTTP(
    settings=switchboard_settings,
    backend_settings=backend_settings,
    switchboard=switchboard,
)
canarytokens_httpd.service.setServiceParent(application)

canarytokens_smtp = ChannelSMTP(
    switchboard_settings=switchboard_settings,
    backend_settings=backend_settings,
    switchboard=switchboard,
)
canarytokens_smtp.service.setServiceParent(application)

canarytokens_kubeconfig = ChannelKubeConfig(
    switchboard_settings=switchboard_settings,
    backend_settings=backend_settings,
    switchboard=switchboard,
)
canarytokens_kubeconfig.service.setServiceParent(application)

canarytokens_mysql = ChannelMySQL(
    port=switchboard_settings.CHANNEL_MYSQL_PORT,
    switchboard=switchboard,
    backend_scheme=backend_settings.BACKEND_SCHEME,
    backend_hostname=backend_settings.BACKEND_HOSTNAME,
)
canarytokens_mysql.service.setServiceParent(application)

canarytokens_wireguard = ChannelWireGuard(
    port=switchboard_settings.CHANNEL_WIREGUARD_PORT,
    switchboard=switchboard,
    backend_scheme=backend_settings.BACKEND_SCHEME,
    backend_hostname=backend_settings.BACKEND_HOSTNAME,
    switchboard_settings=switchboard_settings,
)
canarytokens_wireguard.service.setServiceParent(application)

# loop to update tor exit nodes every 30 min
loop_http = internet.task.LoopingCall(update_tor_exit_nodes_loop)
loop_http.start(1800)
