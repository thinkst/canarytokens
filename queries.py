import re
import requests
import datetime
import simplejson
import urllib
import base64
import settings
from exception import LinkedInFailure
from redismanager import db, KEY_CANARYDROP, KEY_CANARY_DOMAINS,\
     KEY_CANARY_PATH_ELEMENTS, KEY_CANARY_PAGES, KEY_CANARYDROPS_TIMELINE,\
     KEY_USER_ACCOUNT, KEY_CANARYTOKEN_ALERT_COUNT, KEY_IMGUR_TOKEN, \
     KEY_IMGUR_TOKENS, KEY_LINKEDIN_ACCOUNT, KEY_LINKEDIN_ACCOUNTS,\
     KEY_BITCOIN_ACCOUNTS, KEY_BITCOIN_ACCOUNT, KEY_CANARY_NXDOMAINS,\
     KEY_CLONEDSITE_TOKEN, KEY_CLONEDSITE_TOKENS, KEY_CANARY_IP_CACHE, \
     KEY_CANARY_GOOGLE_API_KEY, KEY_TOR_EXIT_NODES, KEY_WEBHOOK_IDX, KEY_EMAIL_IDX, \
     KEY_EMAIL_BLOCK_LIST, KEY_DOMAIN_BLOCK_LIST, KEY_WIREGUARD_KEYMAP, \
     KEY_KUBECONFIG_SERVEREP, KEY_KUBECONFIG_CERTS, KEY_KUBECONFIG_HITS

from twisted.logger import Logger
log = Logger()
from twisted.web.client import getPage



def get_canarydrop(canarytoken=None):
    canarydrop = db.hgetall(KEY_CANARYDROP+canarytoken)
    if 'triggered_list' in canarydrop.keys():
        canarydrop['triggered_list'] = simplejson.loads(canarydrop['triggered_list'])
    return canarydrop

def get_all_canary_sites():
    return ['http://'+x for x in get_all_canary_domains()]

def get_all_canary_path_elements():
    return list(db.smembers(KEY_CANARY_PATH_ELEMENTS))

def add_canary_path_element(path_element=None):
    if not path_element:
        raise ValueError

    return db.sadd(KEY_CANARY_PATH_ELEMENTS, path_element)

def get_all_canary_pages():
    return list(db.smembers(KEY_CANARY_PAGES))

def add_canary_page(page=None):
    if not page:
        raise ValueError

    return db.sadd(KEY_CANARY_PAGES, page)

def get_all_canary_domains():
    return list(db.smembers(KEY_CANARY_DOMAINS))

def get_all_canary_nxdomains():
    return list(db.smembers(KEY_CANARY_NXDOMAINS))

def get_canary_google_api_key():
    return db.get(KEY_CANARY_GOOGLE_API_KEY)

def add_canary_domain(domain=None):
    if not domain:
        raise ValueError

    return db.sadd(KEY_CANARY_DOMAINS, domain)

def add_canary_nxdomain(domain=None):
    if not domain:
        raise ValueError

    return db.sadd(KEY_CANARY_NXDOMAINS, domain)

def add_canary_google_api_key(key=None):
    if not key:
        return None

    return db.set(KEY_CANARY_GOOGLE_API_KEY, key)

def add_email_token_idx(email, canarytoken):
   return db.sadd(KEY_EMAIL_IDX+email, canarytoken)

def add_webhook_token_idx(webhook, canarytoken):
   return db.sadd(KEY_WEBHOOK_IDX+webhook, canarytoken)

def delete_email_tokens(email_address):
    for token in db.smembers(KEY_EMAIL_IDX+email_address):
        db.delete(KEY_CANARYDROP+token)
    # delete idx set
    db.delete(KEY_EMAIL_IDX+email_address)

def delete_webhook_tokens(webhook):
    for token in db.smembers(KEY_WEBHOOK_IDX+webhook):
        db.delete(KEY_CANARYDROP+token)
    # delete idx set
    db.delete(KEY_WEBHOOK_IDX+webhook)

def list_email_tokens(email_address):
    return db.smembers(KEY_EMAIL_IDX+email_address)

def list_webhook_tokens(webhook):
    return db.smembers(KEY_WEBHOOK_IDX+webhook)

def save_canarydrop(canarydrop=None):
    """Persist a Canarydrop into the Redis instance.
       Arguments:
       canarydrop -- Canarydrop object.
    """
    if not canarydrop:
        raise ValueError

    canarytoken = canarydrop.canarytoken

    db.hmset(KEY_CANARYDROP+canarytoken.value(), canarydrop.serialize())

    log.info('Saved canarydrop: {canarydrop}'.format(
                                    canarydrop=canarydrop.serialize()))

    #if the canarydrop is new, save to the timeline
    if db.zscore(KEY_CANARYDROPS_TIMELINE, canarytoken.value()) == None:
        current_time = datetime.datetime.utcnow().strftime("%s.%f")
        db.zadd(KEY_CANARYDROPS_TIMELINE, current_time, canarytoken.value())

    if canarydrop['alert_email_recipient']:
            add_email_token_idx(canarydrop['alert_email_recipient'],canarytoken.value())

    if canarydrop['alert_webhook_url']:
        add_webhook_token_idx(canarydrop['alert_webhook_url'],canarytoken.value())

def get_canarydrop_triggered_list(canarytoken):
    """
    Returns the triggered list for a Canarydrop, or {} if it does not exist
    """
    key = KEY_CANARYDROP+canarytoken.value()
    triggered_list = db.hget(key,'triggered_list')
    if not triggered_list:
        triggered_list={}
    else:
        triggered_list = simplejson.loads(triggered_list)
        #we limit to last N hits, configurable via CANARY_MAX_HISTORY envvar
        triggered_list = {k:v for k,v in triggered_list.iteritems()
                          if k in sorted(triggered_list.keys())[-settings.MAX_HISTORY:]}
    return triggered_list

def add_canarydrop_hit(canarytoken,input_channel,hit_time=None,**kwargs):
    """Add a hit to a canarydrop
       Arguments:
       canarytoken -- canarytoken object.
       **kwargs   -- Additional details about the hit.
    """
    triggered_list = get_canarydrop_triggered_list(canarytoken)

    triggered_key = hit_time if hit_time else datetime.datetime.utcnow().strftime("%s.%f")
    triggered_list[triggered_key] = kwargs
    triggered_list[triggered_key]['input_channel'] = input_channel
    if kwargs.get('src_data', None) and 'aws_keys_event_source_ip' in kwargs['src_data']:
        triggered_list[triggered_key]['geo_info'] = get_geoinfo(kwargs['src_data']['aws_keys_event_source_ip'])
        triggered_list[triggered_key]['is_tor_relay'] = is_tor_relay(kwargs['src_data']['aws_keys_event_source_ip'])
    elif kwargs.get('src_ip', None):
        triggered_list[triggered_key]['geo_info'] = get_geoinfo(kwargs['src_ip'])
        triggered_list[triggered_key]['is_tor_relay'] = is_tor_relay(kwargs['src_ip'])
    db.hset(KEY_CANARYDROP+canarytoken.value(), 'triggered_list',simplejson.dumps(triggered_list))
    return triggered_key

def add_additional_info_to_hit(canarytoken,hit_time,additional_info=None):
    try:
        if not additional_info:
            return

        triggered_list = get_canarydrop_triggered_list(canarytoken)

        if 'additional_info' not in triggered_list[hit_time]:
            triggered_list[hit_time]['additional_info'] = {}
        for k,v in additional_info.iteritems():
            if k in triggered_list[hit_time]['additional_info'].keys():
                triggered_list[hit_time]['additional_info'][k].update(v)
            else:
                triggered_list[hit_time]['additional_info'][k] = v
        db.hset(KEY_CANARYDROP+canarytoken.value(), 'triggered_list',simplejson.dumps(triggered_list))
    except Exception as e:
        log.error('Failed adding additional info: {err}'.format(err=e))

def get_aws_keys(token=None, server=None):
    if not (token or server) or len(token)==0 or len(server)==0:
        log.error('Empty values passed through to get_aws_keys function.')
        return False
    try:
        # data = base64.b64encode('U:'+server+':'+token)
        # The following is because aws username can only be 64 characters long
        if not validate_hostname(server):
            return False

        data = server+'@@'+token
        if len(data)>64:
            log.error('Length of the Server Name and token is too long. Will not work on AWS')
            return False

        url = str(settings.AWSID_URL)

        resp = requests.get('{url}?data={d}'.format(url=url,d=data))
        if not resp:
            log.error('Bad response from getting aws keys')
            return False
        resp_json = resp.json()
        access_key_id = resp_json['access_key_id']
        secret_access_key = resp_json['secret_access_key']
        region = "us-east-2"
        output = "json"
        return (access_key_id, secret_access_key, region, output)
    except Exception as e:
        log.error('Error getting aws keys: {err}'.format(err=e))
        return False

def get_azure_id(token=None, server=None):
    if not (token or server) or len(token)==0 or len(server)==0:
        log.error('Empty values passed through to get_azure_id function.')
        return False
    try:
        token_url = str(settings.AZURE_ID_TOKEN_URL)
        token_auth = str(settings.AZURE_ID_TOKEN_AUTH)

        if token_url == '':
            log.error('No URL provided for AZURE ID creation')
            return False

        if token_auth == '':
            log.error('No AUTH token provided for AZURE ID creation')
            return False

        url = '{token_url}?code={token_auth}'.format(token_url=token_url, token_auth=token_auth)
        data = {
            'token': token,
            'domain': server
        }

        resp = requests.post(url=url, json=data)
        if not resp:
            log.error('Bad response from getting AZURE ID')
            return False
        resp_json = resp.json()
        app_id = resp_json['app_id']
        cert = resp_json['cert']
        tenant_id = resp_json['tenant_id']
        cert_name = resp_json['cert_name']
        return (app_id, cert, tenant_id, cert_name)
    except Exception as e:
        log.error('Error getting azure id: {err}'.format(err=e))
        return False



def validate_hostname(hostname):
    import re
    print 'Going to search {e} for bad username characters'.format(e=hostname)
    pattern = re.compile("[^a-zA-Z0-9+=,.@_-]")
    match = pattern.search(hostname)
    if match:
        log.error('Hostname contains a bad character for AWS username {m} ... aborting'.format(m=match.group(0)))
        return False
    else:
        return True

def get_geoinfo(ip):
    if is_ip_cached(ip):
        return get_geoinfo_from_cache(ip)
    else:
        try:
            resp = get_geoinfo_from_ip(ip)
            add_ip_to_cache(ip, resp)
            return resp
        except Exception as e:
            log.warn('Error getting geo ip: {err}'.format(err=e))
            return ""

def get_geoinfo_from_ip(ip):
    if not settings.IPINFO_API_KEY:
        resp = requests.get('http://ipinfo.io/' + ip + '/json')
    else:
        resp = requests.get('http://ipinfo.io/'+ip+'/json/', auth=(settings.IPINFO_API_KEY,''))
    if resp.status_code != 200:
        raise Exception('ipinfo.io response was unexpected: {resp}'\
                    .format(resp=resp))
    return resp.json()


def get_geoinfo_from_cache(ip):
    key = KEY_CANARY_IP_CACHE + ip
    return simplejson.loads(db.get(key))

def is_ip_cached(ip):
    key = KEY_CANARY_IP_CACHE + ip
    check = db.exists(key)
    if check == 1:
        return True
    return False

def add_ip_to_cache(ip, geoinfo , exp_time=60*60*24):
    """Adds an IP with Geo Data to redis.
       Arguments:
       exp_time -- Expiry time for this IP (in seconds). Default set to 1 day.
    """
    key = KEY_CANARY_IP_CACHE + ip
    db.setex(key,exp_time,simplejson.dumps(geoinfo))

def get_canarydrops(min_time='-inf', max_time='+inf'):
    """Return a list of stored Canarydrops.
       Arguments:
       min_time -- Limit to Canarydrops created after min_time. Format is Unix
                   epoch. Default is no limit.
       max_time -- Limit to Canarydrops created before max_time. Format is Unix
                   epoch. Default is no limit.
    """
    canarydrops = []
    for canarytoken in db.zrangebyscore(KEY_CANARYDROPS_TIMELINE, min_time,
        max_time):
        canarydrops.append(Canarydrop(**get_canarydrop(canarytoken=canarytoken)))
    return canarydrops

def get_canarydrops_array(min_time='-inf', max_time='+inf'):
    """Return an array of stored Canarydrops.
           Arguments:
           min_time -- Limit to Canarydrops created after min_time. Format is Unix
                       epoch. Default is no limit.
           max_time -- Limit to Canarydrops created before max_time. Format is Unix
                       epoch. Default is no limit.
        """
    canarydrops = []
    for canarytoken in db.zrangebyscore(KEY_CANARYDROPS_TIMELINE, min_time,
                                        max_time):
        canarydrops.append(get_canarydrop(canarytoken=canarytoken))
    return canarydrops

def load_user(username):
    """Return a User object.
       Arguments:
       username -- A username.
    """
    account_key = KEY_USER_ACCOUNT+username
    if not db.exists(account_key):
        return None

    from users import User
    return User(db.hgetall(account_key))


def lookup_canarytoken_alert_count(canarytoken):
    key = KEY_CANARYTOKEN_ALERT_COUNT+canarytoken.value()
    return db.get(key)

def save_canarytoken_alert_count(canarytoken, count, expiry):
    key = KEY_CANARYTOKEN_ALERT_COUNT+canarytoken.value()
    db.setex(key, expiry, count)

def save_clonedsite_token(clonedsite_token):
    if not clonedsite_token.get('canarytoken'):
        raise Exception('Cannot save an imgur token without a canarydrop')

    key = KEY_CLONEDSITE_TOKEN+clonedsite_token['clonedsite']+':'+\
          clonedsite_token['canarytoken']
    db.hmset(key, clonedsite_token)
    db.sadd(KEY_CLONEDSITE_TOKENS, key)
    return key

def get_imgur_count(imgur_id=None):
    resp = requests.get('http://imgur.com/ajax/views?images={imgur_id}'\
                        .format(imgur_id=imgur_id))
    resp = resp.json()
    if not resp['success'] or resp['status'] != 200:
        raise Exception('Imgur response was unexpected: {resp}'\
                        .format(resp=resp))
    return resp['data'][imgur_id]

def save_imgur_token(imgur_token):
    if not imgur_token.get('canarytoken'):
        raise Exception('Cannot save an imgur token without a canarydrop')

    if not imgur_token.get('count', None):
        imgur_token['count'] = get_imgur_count(imgur_id=imgur_token['id'])

    key = KEY_IMGUR_TOKEN+imgur_token['id']
    db.hmset(key, imgur_token)
    db.sadd(KEY_IMGUR_TOKENS, key)
    return key

def get_all_imgur_tokens():
    all_imgur_tokens = []
    for key in db.smembers(KEY_IMGUR_TOKENS):
        all_imgur_tokens.append(db.hgetall(key))
        all_imgur_tokens[-1]['count'] = int(all_imgur_tokens[-1]['count'])
    return all_imgur_tokens

def get_linkedin_viewer_count(username=None, password=None):
    from twill import get_browser
    from twill.commands import add_extra_header, go, fv, submit, reset_browser
    reset_browser()
    from twill.errors import TwillException
    add_extra_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36')
    go("https://www.linkedin.com/nhome/")
    # Added because LinkedIn login page no longer names the login form.
    b = get_browser()
    form_num = ''
    for n, f in enumerate(b.get_all_forms()):
        try:
            b.get_form_field(f, "session_key")
            b.get_form_field(f, "session_password")
            form_num = str(n+1)
        except TwillException:
            pass
    if form_num == '':
        log.error('Failed to parse LinkedIn login page - page format may have changed.')
        raise LinkedInFailure()
    #fv("login", 'session_password', 'LetsTryPrime')
    #fv("login", 'session_key', 'ms_DerrickWortham@endian.co.za')
    fv(form_num, 'session_key', username)
    fv(form_num, 'session_password', password)
    submit()
    go('http://www.linkedin.com/wvmx/profile?trk=nav_responsive_sub_nav_wvmp')

    try:
        for i in get_browser().result.lxml\
                .get_element_by_id('viewers_list-content')\
                .iterchildren():
            user_listing = simplejson.loads(i.text.replace('\\u002d','-'))
    except Exception as e:
        log.error('Failed to extract user_listing from page: {error}'.format(error=e))
        raise LinkedInFailure()

    try:
        current_count = user_listing['content']['wvmx_profile_viewers']['viewersCount']
        return current_count
    except KeyError:
        log.error('Profile view struct in unknown format: {user_listing}'.format(user_listing=user_listing))
        raise LinkedInFailure()

def get_linkedin_account(username_key=None, username=None):
    if username:
        username_key=KEY_LINKEDIN_ACCOUNT+username

    data = db.hgetall(username_key)
    try:
        data['count'] = int(data['count'])
    except KeyError:
        data['count'] = -1
    return data

def get_all_linkedin_accounts():
    all_linkedin_accounts = []
    for key in db.smembers(KEY_LINKEDIN_ACCOUNTS):
        all_linkedin_accounts.append(get_linkedin_account(username_key=key))
    return all_linkedin_accounts

def create_linkedin_account(username=None, password=None, canarydrop=None):

    key = KEY_LINKEDIN_ACCOUNT+username

    if db.exists(key):
        raise KeyError

    if not canarydrop:
        from tokens import Canarytoken
        from canarydrop import Canarydrop
        ht = Canarytoken()
        canarydrop = Canarydrop(canarytoken=ht.value())
    else:
        ht = canarydrop.canarytoken

    canarydrop['linkedin_username'] = username
    save_canarydrop(canarydrop=canarydrop)

    linkedin_account = {
        'username': username.lower(),
        'password': password,
        'canarytoken': ht.value(),
        'count': get_linkedin_viewer_count(
                                    username=username,
                                    password=password)}

    return save_linkedin_account(linkedin_account=linkedin_account)

def save_linkedin_account(linkedin_account=None):
    if not linkedin_account.get('canarytoken'):
        raise Exception('Cannot save an LinkedIn account without a canarydrop')

    key = KEY_LINKEDIN_ACCOUNT+linkedin_account['username']
    db.hmset(key, linkedin_account)
    db.sadd(KEY_LINKEDIN_ACCOUNTS, key)
    return key

def get_bitcoin_account(address_key=None, address=None):
    if address:
        address_key=KEY_BITCOIN_ACCOUNT+address

    data = db.hgetall(address_key)
    try:
        data['balance'] = int(data['balance'])
    except KeyError:
        data['balance'] = -1
    return data

def get_all_bitcoin_accounts():
    all_bitcoin_accounts = []
    for key in db.smembers(KEY_BITCOIN_ACCOUNTS):
        all_bitcoin_accounts.append(get_bitcoin_account(address_key=key))
    return all_bitcoin_accounts

def get_bitcoin_address_balance(address=None):
    resp = requests.get('https://blockchain.info/q/addressbalance/{address}'\
                        .format(address=address))

    if resp.status_code != 200:
        raise Exception('Bitcoin response was unexpected: {resp}'\
                        .format(resp=resp))
    try:
        return int(resp.content)
    except ValueError:
        raise Exception('Bitcoin response was unexpected: {resp}'\
                        .format(resp=resp))

def create_bitcoin_account(address=None, canarydrop=None):

    key = KEY_BITCOIN_ACCOUNT+address

    if db.exists(key):
        raise KeyError

    if not canarydrop:
        from tokens import Canarytoken
        from canarydrop import Canarydrop
        ht = Canarytoken()
        canarydrop = Canarydrop(canarytoken=ht.value())
    else:
        ht = canarydrop.canarytoken

    canarydrop['bitcoin_account'] = address
    save_canarydrop(canarydrop=canarydrop)

    bitcoin_account = {
        'canarytoken': ht.value(),
        'address': address,
        'balance': get_bitcoin_address_balance(
                                    address=address)}

    return save_bitcoin_account(bitcoin_account=bitcoin_account)

def save_bitcoin_account(bitcoin_account=None):
    if not bitcoin_account.get('canarytoken'):
        raise Exception('Cannot save an Bitcoin account without a canarydrop')

    key = KEY_BITCOIN_ACCOUNT+bitcoin_account['address']
    db.hmset(key, bitcoin_account)
    db.sadd(KEY_BITCOIN_ACCOUNTS, key)
    return key

def is_webhook_valid(url):
    """Tests if a webhook is valid by sending a test payload
       Arguments:
       url -- Webhook url
    """
    if not url or url == '':
        return False

    slack_hook_base_url = "https://hooks.slack.com"
    googlechat_hook_base_url = "https://chat.googleapis.com/"
    if (slack_hook_base_url in url or googlechat_hook_base_url in url):
        payload = {'text': 'Validating new canarytokens webhook'}
    else:
        payload = {"manage_url": "http://example.com/test/url/for/webhook",
                   "memo": "Congrats! The newly saved webhook works",
                   "additional_data": {
                        "src_ip": "1.1.1.1",
                        "useragent": "Mozilla/5.0...",
                        "referer": "http://example.com/referrer",
                        "location": "http://example.com/location"
                    },
               "channel": "HTTP",
               "time": datetime.datetime.now().strftime('%Y-%m-%d %T') }
    try:
        response = requests.post(url,
                                 simplejson.dumps(payload),
                                 headers={'content-type': 'application/json'},
                                 timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.Timeout as e:
        log.error('Timed out sending test payload to webhook: {url}'.format(url=url))
        return False
    except requests.exceptions.RequestException as e:
        log.error('Failed sending test payload to webhook: {url} with error {error}'.format(url=url,error=e))
        return False

def is_valid_email(email):
    # This validation checks that no disallowed characters are in the section of the email
    # address before the @
    #Ripped from https://www.regular-expressions.info/email.html
    regex = re.compile(r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
    match = regex.search(email.lower())
    if not match:
        return False
    else:
        return True

def normalize_email(email):
    [user, domain] = email.split('@')
    if domain in ['gmail.com', 'googlemail.com', 'google.com']:
        delabelled = user.split('+')[0]
        san_user = delabelled.replace('.', '')
        return '{}@{}'.format(san_user, domain)
    else:
        return email

def block_email(email):
    san = normalize_email(email)
    db.sadd(KEY_EMAIL_BLOCK_LIST, san)

def unblock_email(email):
    san = normalize_email(email)
    db.srem(KEY_EMAIL_BLOCK_LIST, san)

def block_domain(domain):
    db.sadd(KEY_DOMAIN_BLOCK_LIST, domain)

def unblock_domain(domain):
    db.srem(KEY_DOMAIN_BLOCK_LIST, domain)

def is_email_blocked(email):
    san = normalize_email(email)
    domain = email.split('@')[1]
    return db.sismember(KEY_DOMAIN_BLOCK_LIST, domain) or db.sismember(KEY_EMAIL_BLOCK_LIST, san)

def is_tor_relay(ip):
    if not db.exists(KEY_TOR_EXIT_NODES):
        update_tor_exit_nodes_loop()
    return db.sismember(KEY_TOR_EXIT_NODES, simplejson.dumps(ip))

def update_tor_exit_nodes(contents):
    if "ExitAddress" in contents:
        db.delete(KEY_TOR_EXIT_NODES)
    for line in contents.splitlines():
        if 'ExitAddress' in line:
            db.sadd(KEY_TOR_EXIT_NODES, simplejson.dumps(line.split(' ')[1]))

def update_tor_exit_nodes_loop():
    d = getPage('https://check.torproject.org/exit-addresses')
    d.addCallback(update_tor_exit_nodes)

def get_certificate(key, _type=None):
    certificate = db.hgetall("{}{}".format(KEY_KUBECONFIG_CERTS, key))
    if certificate is not None and _type is not None:
        return certificate.get(_type, None)

    return certificate

def save_certificate(key, cert_obj):
    db.hmset("{}{}".format(KEY_KUBECONFIG_CERTS, key), cert_obj)

def save_kc_endpoint(endpoint):
    db.set(KEY_KUBECONFIG_SERVEREP, endpoint)

def get_kc_endpoint():
    return db.get(KEY_KUBECONFIG_SERVEREP)

def save_kc_hit_for_aggregation(key, hits, update=False):
    hit_key = "{}{}".format(KEY_KUBECONFIG_HITS, key)
    db.hset(hit_key, 'hits', hits)

    if not update:
        # typical timeout sent with each kubectl caching discovery request is 32s, and 5 requests are sent as part of each kubectl execution
        db.expire(hit_key, 5*32)

def get_kc_hits(key):
    return (db.hgetall("{}{}".format(KEY_KUBECONFIG_HITS, key)), db.pttl("{}{}".format(KEY_KUBECONFIG_HITS, key)))

def wireguard_keymap_add(public_key, canarytoken):
    db.hset(KEY_WIREGUARD_KEYMAP, public_key, canarytoken)

def wireguard_keymap_del(public_key):
    db.hdel(KEY_WIREGUARD_KEYMAP, public_key)

def wireguard_keymap_get(public_key):
    return db.hget(KEY_WIREGUARD_KEYMAP, public_key)
