import os
import sys
settingsmodule = sys.modules[__name__]

DEBUG=False

LISTEN_DOMAIN=""

if DEBUG:
    CHANNEL_DNS_PORT=5354
    CHANNEL_HTTP_PORT=8083
    CHANNEL_SMTP_PORT=2500
    CHANNEL_MYSQL_PORT=6033
else:
    CHANNEL_HTTP_PORT=8083
    CHANNEL_SMTP_PORT=25
    CHANNEL_DNS_PORT=53
    CHANNEL_MYSQL_PORT=3306

CHANNEL_MTLS_KUBECONFIG_PORT=6443

CHANNEL_LINKEDIN_MIN_DELAY=60*60*24
CHANNEL_IMGUR_MIN_DELAY=60*60
CHANNEL_BITCOIN_MIN_DELAY=60*60

CANARYTOKENS_HTTP_PORT=8082

CANARY_PDF_TEMPLATE="templates/template.pdf"
CANARY_PDF_TEMPLATE_OFFSET=793
CANARY_WORD_TEMPLATE="templates/template.docx"
CANARY_MYSQL_DUMP_TEMPLATE="templates/mysql_tables.zip"
CANARY_EXCEL_TEMPLATE="templates/template.xlsx"

TOKEN_RETURN="gif" #could be gif, fortune

MAX_UPLOAD_SIZE=1024 * 1024 * 1
WEB_IMAGE_UPLOAD_PATH='/uploads'

for envvar in ['SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_SERVER', 'AWSID_URL',
               'MAILGUN_DOMAIN_NAME', 'MAILGUN_API_KEY','MAILGUN_BASE_URL','MANDRILL_API_KEY','SENDGRID_API_KEY',
               'PUBLIC_IP','PUBLIC_DOMAIN','ALERT_EMAIL_FROM_ADDRESS','ALERT_EMAIL_FROM_DISPLAY',
               'ALERT_EMAIL_SUBJECT','DOMAINS','NXDOMAINS', 'TOKEN_RETURN', 'MAX_UPLOAD_SIZE',
               'WEB_IMAGE_UPLOAD_PATH', 'DEBUG', 'IPINFO_API_KEY', 'SWITCHBOARD_LOG_COUNT',
               'SWITCHBOARD_LOG_SIZE', 'FRONTEND_LOG_COUNT', 'FRONTEND_LOG_SIZE', 'MAX_HISTORY',
               'MAX_ALERTS_PER_MINUTE', 'WG_PRIVATE_KEY_SEED', 'WG_PRIVATE_KEY_N', 'DEV_BUILD_ID',
               'CACHED_DNS_REQUEST_PERIOD', 'AZURE_ID_TOKEN_URL', 'AZURE_ID_TOKEN_AUTH']:
    try:
        setattr(settingsmodule, envvar, os.environ['CANARY_'+envvar])
    except KeyError:
        if not hasattr(settingsmodule, envvar):
            setattr(settingsmodule, envvar, '')

if getattr(settingsmodule, 'AWSID_URL') == '':
    setattr(settingsmodule, 'AWSID_URL', "https://1luncdvp6l.execute-api.us-east-2.amazonaws.com/prod/CreateUserAPITokens")

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

try:
    setattr(settingsmodule, 'ERROR_LOG_WEBHOOK', os.environ['ERROR_LOG_WEBHOOK'])
except KeyError:
    pass
    # Do not set this an an attribute if it is not in the config / os environ

for log_config in ['SWITCHBOARD_LOG_COUNT', 'SWITCHBOARD_LOG_SIZE', 'FRONTEND_LOG_COUNT',
        'FRONTEND_LOG_SIZE']:
    val = getattr(settingsmodule, log_config)
    if log_config.endswith('COUNT') and val == '':
        val = 5
    elif log_config.endswith('SIZE') and val == '':
        val = 5000000

    setattr(settingsmodule, log_config, int(val))

# Configure the caching period for deduplicating DNS requests. Default period is 10
try:
    setattr(settingsmodule, 'CACHED_DNS_REQUEST_PERIOD', int(getattr(settingsmodule, 'CACHED_DNS_REQUEST_PERIOD')))
except:
    setattr(settingsmodule, 'CACHED_DNS_REQUEST_PERIOD', 10)

# Configure the maximum number of saved hits on any token. Default list size is 10
try:
    setattr(settingsmodule, 'MAX_HISTORY', int(getattr(settingsmodule, 'MAX_HISTORY'))-1)
except:
    setattr(settingsmodule, 'MAX_HISTORY', 9) # The off-by-one is intentional, due to Python slicing notation

try:
    setattr(settingsmodule, 'PROTOCOL', os.environ['PROTOCOL'])
except KeyError:
    if not hasattr(settingsmodule, 'PROTOCOL'):
        setattr(settingsmodule, 'PROTOCOL', 'http')

if WEB_IMAGE_UPLOAD_PATH and not os.path.exists(WEB_IMAGE_UPLOAD_PATH):
    os.mkdir(WEB_IMAGE_UPLOAD_PATH)

REDIS_HOST='redis'
REDIS_PORT=6379
REDIS_DB='0'

TWILIO_ENABLED=False
TWILIO_FROM_NUMBER=""
TWILIO_ACCOUNT_SID=""
TWILIO_AUTH_TOKEN=""
