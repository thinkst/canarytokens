import redis

import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
#db.DEFAULT_EXPIRY = 120

KEY_CANARYDROP               = 'canarydrop:'
KEY_CANARYDROPS_TIMELINE     = 'canarydrops_timeline:'
KEY_CANARY_DOMAINS           = 'canary_domains'
KEY_CANARY_NXDOMAINS         = 'canary_nxdomains'
KEY_CANARY_PATH_ELEMENTS     = 'canary_path_elements'
KEY_CANARY_PAGES             = 'canary_pages'
KEY_USER_ACCOUNT            = 'account:'
KEY_CANARYTOKEN_ALERT_COUNT  = 'canarytoken_alert_count:'
KEY_IMGUR_TOKEN             = 'imgur_token:'
KEY_IMGUR_TOKENS            = 'imgur_tokens'
KEY_LINKEDIN_ACCOUNTS       = 'linkedin_accounts'
KEY_LINKEDIN_ACCOUNT        = 'linkedin_account:'
KEY_BITCOIN_ACCOUNTS        = 'bitcoin_accounts'
KEY_BITCOIN_ACCOUNT         = 'bitcoin_account:'
