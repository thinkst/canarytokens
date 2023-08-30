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
# fmt: off
CANARYTOKEN_ALPHABET = ['0', '1', '2', '3', '4', '5',
                        '6', '7', '8', '9', 'a', 'b',
                        'c', 'd', 'e', 'f', 'g', 'h',
                        'i', 'j', 'k', 'l', 'm', 'n',
                        'o', 'p', 'q', 'r', 's', 't',
                        'u', 'v', 'w', 'x', 'y', 'z']
# fmt: on
CANARYTOKEN_LENGTH = 25  # equivalent to 128-bit id

CANARY_PDF_TEMPLATE_OFFSET: int = 793

MAILGUN_SENT_STATUS = ["ignored", "success", "failed"]
MAILGUN_IGNORE_ERRORS = [
    "to parameter is not a valid address. please check documentation"
]
