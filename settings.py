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

for envvar in ['MAILGUN_DOMAIN_NAME','MAILGUN_API_KEY','MANDRILL_API_KEY',
               'PUBLIC_IP','ALERT_EMAIL_FROM_ADDRESS','ALERT_EMAIL_FROM_DISPLAY',
               'ALERT_EMAIL_SUBJECT','DOMAINS','NXDOMAINS']:
    try:
        setattr(settingsmodule, envvar, os.environ['CANARY_'+envvar])
    except KeyError:
        setattr(settingsmodule, envvar, '')

for envvar in ['DOMAINS', 'NXDOMAINS']:
    try:
        setattr(settingsmodule, envvar, os.environ['CANARY_'+envvar].split(','))
    except KeyError:
        setattr(settingsmodule, envvar, [])

PUBLIC_DOMAIN=DOMAINS[0]

REDIS_HOST='redis'
REDIS_PORT=6379
REDIS_DB='0'

TWILIO_ENABLED=False
TWILIO_FROM_NUMBER=""
TWILIO_ACCOUNT_SID=""
TWILIO_AUTH_TOKEN=""
