import sys, os
import logging
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from twisted.names import server
from twisted.application import service, internet

from httpd_site import CanarytokensHttpd
from switchboard import Switchboard

import setup_db

from twisted.logger import ILogObserver, textFileLogObserver
from twisted.python import logfile
import settings

logging.basicConfig()
logger = logging.getLogger('generator_httpd')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger.debug('Canarydrops generator HTTPd')

application = service.Application("Canarydrops Generator Web Server")
f = logfile.LogFile.fromFullPath(settings.LOG_FILE, rotateLength=5000000, maxRotatedFiles=5)
application.setComponent(ILogObserver, textFileLogObserver(f))

canarytokens_httpd = CanarytokensHttpd(port=settings.CANARYTOKENS_HTTP_PORT)
canarytokens_httpd.service.setServiceParent(application)
