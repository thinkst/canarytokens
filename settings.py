import os
import sys
settingsmodule = sys.modules[__name__]

DEBUG=False

LISTEN_DOMAIN=""

if DEBUG:
    CHANNEL_DNS_PORT=5354
    CHANNEL_HTTP_PORT=8083
    CHANNEL_SMTP_PORT=2500
else:
    CHANNEL_HTTP_PORT=8083
    CHANNEL_SMTP_PORT=25
    CHANNEL_DNS_PORT=53

CHANNEL_LINKEDIN_MIN_DELAY=60*60*24
CHANNEL_IMGUR_MIN_DELAY=60*60
CHANNEL_BITCOIN_MIN_DELAY=60*60

CANARYTOKENS_HTTP_PORT=8082

CANARY_PDF_TEMPLATE="templates/template.pdf"
CANARY_PDF_TEMPLATE_OFFSET=793
CANARY_WORD_TEMPLATE="templates/template.docx"

TOKEN_RETURN="gif" #could be gif, fortune

MAX_UPLOAD_SIZE=1024 * 1024 * 1
WEB_IMAGE_UPLOAD_PATH='/uploads'

for envvar in ['SMTP_PORT', 'SMTP_PASSWORD', 'SMTP_SERVER', 'MAILGUN_DOMAIN_NAME',
               'MAILGUN_API_KEY','MANDRILL_API_KEY','SENDGRID_API_KEY',
               'PUBLIC_IP','PUBLIC_DOMAIN','ALERT_EMAIL_FROM_ADDRESS','ALERT_EMAIL_FROM_DISPLAY',
               'ALERT_EMAIL_SUBJECT','DOMAINS','NXDOMAINS', 'TOKEN_RETURN', 'MAX_UPLOAD_SIZE',
               'WEB_IMAGE_UPLOAD_PATH', 'DEBUG']:
    try:
        setattr(settingsmodule, envvar, os.environ['CANARY_'+envvar])
    except KeyError:
        if not hasattr(settingsmodule, envvar):
            setattr(settingsmodule, envvar, '')

if type(DEBUG) == str:
    DEBUG = (DEBUG == "True")

for envvar in ['DOMAINS', 'NXDOMAINS','GOOGLE_API_KEY']:
    try:
        setattr(settingsmodule, envvar, os.environ['CANARY_'+envvar].split(','))
    except KeyError:
        setattr(settingsmodule, envvar, [])

try:
    setattr(settingsmodule, 'LOG_FILE', os.environ['LOG_FILE'])
except KeyError:
    if not hasattr(settingsmodule, 'LOG_FILE'):
        setattr(settingsmodule, 'LOG_FILE', [])

if WEB_IMAGE_UPLOAD_PATH and not os.path.exists(WEB_IMAGE_UPLOAD_PATH):
    os.mkdir(WEB_IMAGE_UPLOAD_PATH)

REDIS_HOST='redis'
REDIS_PORT=6379
REDIS_DB='0'

TWILIO_ENABLED=False
TWILIO_FROM_NUMBER=""
TWILIO_ACCOUNT_SID=""
TWILIO_AUTH_TOKEN=""
