from twisted.python import log
from twisted.python import logfile
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import settings

def logger():
    f = logfile.LogFile.fromFullPath(settings.LOG_FILE, rotateLength=100000000, maxRotatedFiles=5)
    log_observer = log.FileLogObserver(f)
    return log_observer.emit
