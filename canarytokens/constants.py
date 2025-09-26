OUTPUT_CHANNEL_EMAIL = "Email"
OUTPUT_CHANNEL_WEBHOOK = "Webhook"
OUTPUT_CHANNEL_TWILIO_SMS = "TwilioSMS"

INPUT_CHANNEL_HTTP = "HTTP"
INPUT_CHANNEL_DNS = "DNS"
INPUT_CHANNEL_IMGUR = "Imgur"
INPUT_CHANNEL_LINKEDIN = "LinkedIn"
INPUT_CHANNEL_BITCOIN = "Bitcoin"
INPUT_CHANNEL_SMTP = "SMTP"
INPUT_CHANNEL_MTLS = "Kubeconfig"
INPUT_CHANNEL_MYSQL = "MYSQL"
INPUT_CHANNEL_WIREGUARD = "WireGuard"

# DESIGN: We'll want a constraint on this but what is sensible as a user and what is practical for our system?
MEMO_MAX_CHARACTERS = 1000
CANARYTOKEN_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
CANARYTOKEN_LENGTH = 25  # equivalent to 128-bit id

CANARY_IMAGE_URL = (
    "https://s3-eu-west-1.amazonaws.com/email-images.canary.tools/canary-logo-round.png"
)

CANARY_PDF_TEMPLATE_OFFSET: int = 793


MAILGUN_IGNORE_ERRORS = [
    "to parameter is not a valid address. please check documentation"
]

MAX_WEBHOOK_URL_LENGTH = 1024
WEBHOOK_BASE_URL_SLACK = "https://hooks.slack.com"
WEBHOOK_BASE_URL_GOOGLE_CHAT = "https://chat.googleapis.com"
WEBHOOK_BASE_URL_DISCORD = "https://discord.com/api/webhooks"
WEBHOOK_BASE_URL_REGEX_MS_TEAMS = r"^https://[\w.]+\.webhook\.office\.com/webhookb2/.*"
