from twisted.python import log
from twisted.python import logfile
import settings

def logger():
    f = logfile.LogFile.fromFullPath(settings.LOG_FILE, rotateLength=5000000, maxRotatedFiles=5)
    log_observer = log.FileLogObserver(f)
    return log_observer.emit
