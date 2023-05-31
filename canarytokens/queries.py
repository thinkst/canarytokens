# Design: Queries should be just the redis keys and associated helper functions.
from __future__ import annotations

import base64
import datetime
import json
import secrets
from ipaddress import IPv4Address
from typing import Dict, List, Literal, Optional, Tuple, Union

import requests
from pydantic import EmailStr, HttpUrl, parse_obj_as
from twisted.logger import Logger

from canarytokens import canarydrop as cand
from canarytokens import models, tokens
from canarytokens.exceptions import CanarydropAuthFailure, NoCanarytokenPresent
from canarytokens.redismanager import (  # KEY_BITCOIN_ACCOUNT,; KEY_BITCOIN_ACCOUNTS,; KEY_CANARY_NXDOMAINS,; KEY_CANARYTOKEN_ALERT_COUNT,; KEY_CLONEDSITE_TOKEN,; KEY_CLONEDSITE_TOKENS,; KEY_IMGUR_TOKEN,; KEY_IMGUR_TOKENS,; KEY_KUBECONFIG_CERTS,; KEY_KUBECONFIG_HITS,; KEY_KUBECONFIG_SERVEREP,; KEY_LINKEDIN_ACCOUNT,; KEY_LINKEDIN_ACCOUNTS,; KEY_USER_ACCOUNT,
    DB,
    KEY_AUTH_IDX,
    KEY_CANARY_DOMAINS,
    KEY_CANARY_GOOGLE_API_KEY,
    KEY_CANARY_IP_CACHE,
    KEY_CANARY_NXDOMAINS,
    KEY_CANARY_PAGES,
    KEY_CANARY_PATH_ELEMENTS,
    KEY_CANARY_RETURN_TOKEN,
    KEY_CANARYDROP,
    KEY_CANARYDROPS_TIMELINE,
    KEY_CANARYTOKEN_ALERT_COUNT,
    KEY_EMAIL_IDX,
    KEY_KUBECONFIG_CERTS,
    KEY_KUBECONFIG_SERVEREP,
    KEY_MAIL_TO_SEND,
    KEY_SENT_MAIL_QUEUE,
    KEY_TOR_EXIT_NODES,
    KEY_WEBHOOK_IDX,
    KEY_WIREGUARD_KEYMAP,
)

log = Logger()


def get_canarydrop(canarytoken: tokens.Canarytoken) -> Optional[cand.Canarydrop]:

    canarydrop: dict = DB.get_db().hgetall(KEY_CANARYDROP + canarytoken.value())

    if len(canarydrop) == 0:
        raise NoCanarytokenPresent(f"Failed to find drop for: {canarytoken.value()}")

    if "triggered_details" in canarydrop:
        canarydrop["triggered_details"] = json.loads(
            canarydrop["triggered_details"],
        )
    if "triggered_list" in canarydrop:
        canarydrop["triggered_details"] = json.loads(
            canarydrop.pop("triggered_list"),
        )
        canarydrop["triggered_details"]["token_type"] = canarydrop["type"]
    if "user" in canarydrop.keys():
        # Make user in redis fully supported.
        canarydrop["user"] = models.User(name=canarydrop["user"])

    canarydrop["canarytoken"] = canarytoken
    return cand.Canarydrop(**canarydrop)


def get_canarydrop_from_auth(*, token: str, auth: str) -> cand.Canarydrop:
    """Fetches a drop given a `token` and it's associated `auth`."""
    canarytokens = DB.get_db().smembers(KEY_AUTH_IDX + auth)
    if len(canarytokens) != 1:
        raise CanarydropAuthFailure(
            f"{len(canarytokens)} tokens are associated with this auth. Tokens {canarytokens}"
        )
    canarydrop = get_canarydrop(tokens.Canarytoken(canarytokens.pop()))
    if canarydrop is None:
        raise CanarydropAuthFailure(
            f"{len(canarytokens)} canarydrop associated with this auth is missing. Token(s) {canarytokens}"
        )
    if not secrets.compare_digest(token, canarydrop.canarytoken.value()):
        raise CanarydropAuthFailure(
            f"{len(canarytokens)} canarydrop associated with this auth has inconsistent token. Token(s) {canarytokens}"
        )
    return canarydrop


def get_all_canary_sites():
    return [f"http://{str(o)}" for o in get_all_canary_domains()]


def get_all_canary_path_elements() -> list[str]:
    return list(DB.get_db().smembers(KEY_CANARY_PATH_ELEMENTS))


def add_canary_path_element(path_element: str) -> int:
    return DB.get_db().sadd(KEY_CANARY_PATH_ELEMENTS, path_element)


def get_all_canary_pages() -> List[str]:
    return list(DB.get_db().smembers(KEY_CANARY_PAGES))


def add_canary_page(page: str) -> int:
    return DB.get_db().sadd(KEY_CANARY_PAGES, page)


def get_all_canary_domains():
    # TODO: leave as a set?
    return [o for o in DB.get_db().smembers(KEY_CANARY_DOMAINS)]


def get_all_canary_nxdomains():
    return list(DB.get_db().smembers(KEY_CANARY_NXDOMAINS))


def get_canary_google_api_key():
    return DB.get_db().get(KEY_CANARY_GOOGLE_API_KEY)


def add_canary_domain(domain: str) -> int:
    return DB.get_db().sadd(KEY_CANARY_DOMAINS, domain)


def remove_canary_domain():
    return DB.get_db().delete(KEY_CANARY_DOMAINS)


def add_canary_nxdomain(domain: str) -> int:
    return DB.get_db().sadd(KEY_CANARY_NXDOMAINS, domain)


def add_email_token_idx(email, canarytoken):
    return DB.get_db().sadd(KEY_EMAIL_IDX + email, canarytoken)


def add_webhook_token_idx(webhook: HttpUrl, canarytoken: str) -> int:
    return DB.get_db().sadd(KEY_WEBHOOK_IDX + webhook, canarytoken)


def add_auth_token_idx(auth: str, token: str):
    return DB.get_db().sadd(KEY_AUTH_IDX + auth, token)


def delete_email_tokens(email_address):
    for token in DB.get_db().smembers(KEY_EMAIL_IDX + email_address):
        DB.get_db().delete(KEY_CANARYDROP + token)
    # delete idx set
    DB.get_db().delete(KEY_EMAIL_IDX + email_address)


def delete_webhook_tokens(webhook: str):
    """
    Looks up all tokens associated with `webhook`
    and deletes those canarydrops.

    Args:
        webhook (str): webhook url.
    """
    for token in DB.get_db().smembers(KEY_WEBHOOK_IDX + webhook):
        DB.get_db().delete(KEY_CANARYDROP + token)
    # delete idx set
    DB.get_db().delete(KEY_WEBHOOK_IDX + webhook)


def list_email_tokens(email_address):
    return DB.get_db().smembers(KEY_EMAIL_IDX + email_address)


def list_webhook_tokens(webhook):
    return DB.get_db().smembers(KEY_WEBHOOK_IDX + webhook)


def save_canarydrop(canarydrop: cand.Canarydrop):
    """
    Persist a Canarydrop into the Redis instance.
    Args:
        canarydrop (cand.Canarydrop): canarydrop to persist.
    """

    canarytoken = canarydrop.canarytoken
    DB.get_db().hset(
        KEY_CANARYDROP + canarytoken.value(),
        mapping=canarydrop.serialize(),
    )

    log.info("Saved canarydrop: {canarydrop}", canarydrop=canarydrop.serialize())

    # if the canarydrop is new, save to the timeline
    if DB.get_db().zscore(KEY_CANARYDROPS_TIMELINE, canarytoken.value()) is None:
        current_time = datetime.datetime.utcnow().strftime("%s.%f")
        DB.get_db().zadd(KEY_CANARYDROPS_TIMELINE, {canarytoken.value(): current_time})

    if canarydrop.alert_email_recipient:
        add_email_token_idx(canarydrop.alert_email_recipient, canarytoken.value())

    if canarydrop.alert_webhook_url:
        add_webhook_token_idx(canarydrop.alert_webhook_url, canarytoken.value())

    add_auth_token_idx(canarydrop.auth, canarydrop.canarytoken.value())


# def _v2_compatibility_serialize_canarydrop(serialized_drop:dict[str, str], canarydrop:cand.Canarydrop)->dict[str, str]:
#     # V2 compatibility - timestamp and created_at are aliases
#     serialized_drop["timestamp"] = serialized_drop.pop("created_at")

#     if "triggered_details"  in serialized_drop:
#         triggered_list = {}
#         details = json.loads(serialized_drop["triggered_details"])
#         for hit in details["hits"]:
#             triggered_list[hit[]]
#         if len(details.get("hits", "empty")) == 0:
#             serialized_drop.pop("triggered_details")


def _v2_compatibility_loading_triggered_details(key: str) -> str:
    """Reads the `triggered_list` stored in v2 shape
    and returns `triggered_details` in v3 shape.

    Args:
        key (str): `canarydrop:__token__` to get triggered_details for.

    Returns:
        str: triggered_details in the v3 shape.
    """
    triggered_details_str = DB.get_db().hget(key, "triggered_list")
    if triggered_details_str is None:
        triggered_details_str = "{}"
    token_type = models.TokenTypes(DB.get_db().hget(key, "type"))
    triggered_details = json.loads(triggered_details_str)

    return json.dumps({"token_type": token_type, **triggered_details})


def get_canarydrop_triggered_details(
    canarytoken: tokens.Canarytoken,
    max_history: int = 10,
) -> models.AnyTokenHistory:
    """
    Returns the triggered list for a Canarydrop, or {} if it does not exist
    """
    key = KEY_CANARYDROP + canarytoken.value()
    triggered_details = _v2_compatibility_loading_triggered_details(key=key)

    if not triggered_details:
        triggered_details = {}
    else:
        triggered_details = json.loads(triggered_details)
        token_type = triggered_details.pop("token_type")
        triggered_details = {
            k: v
            for k, v in triggered_details.items()
            if k
            in sorted(
                triggered_details.keys(),
            )[-(max_history):]
        }
        triggered_details["token_type"] = token_type
    return parse_obj_as(models.AnyTokenHistory, triggered_details)


def add_canarydrop_hit(token_hit: models.AnyTokenHit, canarytoken):
    """
    Add a hit to a canarydrop. A hit will capture the
    Arguments:
    canarytoken -- canarytoken object.
    **kwargs   -- Additional details about the hit.
    """
    token_history = get_canarydrop_triggered_details(canarytoken)

    if token_history.token_type != token_hit.token_type:
        # Design: This might not hold in the future but for now this is true.
        raise ValueError(
            f"All hits must be of a single type. Given {token_hit.token_type}; existsing {token_history.token_type}"
        )

    token_history.hits.append(token_hit)

    DB.get_db().hset(
        KEY_CANARYDROP + canarytoken.value(),
        "triggered_list",
        json.dumps(token_history.serialize_for_v2()),
    )
    return token_hit.time_of_hit


# def get_canarydrop_history():

# triggered_details[hit_time] = kwargs
# triggered_details[hit_time]["input_channel"] = input_channel
# if (
#     kwargs.get("src_data", None)
#     and "aws_keys_event_source_ip" in kwargs["src_data"]
# ):
#     triggered_details[hit_time]["geo_info"] = get_geoinfo(
#         kwargs["src_data"]["aws_keys_event_source_ip"],
#     )
#     triggered_details[hit_time]["is_tor_relay"] = is_tor_relay(
#         kwargs["src_data"]["aws_keys_event_source_ip"],
#     )
# elif kwargs.get("src_ip", None):
#     triggered_details[hit_time]["geo_info"] = get_geoinfo(kwargs["src_ip"])
#     triggered_details[hit_time]["is_tor_relay"] = is_tor_relay(kwargs["src_ip"])
# log.info(f"Adding token history: {str(token_history.json())}")
# data = DB.get_db().hgetall(KEY_CANARYDROP + canarytoken.value())
#
# trigger_list = get_canarydrop_triggered_details(canarytoken=canarytoken)
#
# return hit_time


def add_additional_info_to_hit(canarytoken, hit_time, additional_info):
    triggered_details = get_canarydrop_triggered_details(canarytoken)
    enriched_hit = next(
        filter(lambda o: o.time_of_hit == hit_time, triggered_details.hits)
    )
    triggered_details.hits.remove(enriched_hit)
    if isinstance(
        enriched_hit,
        (
            models.SlowRedirectTokenHit,
            models.CustomImageTokenHit,
            models.WebBugTokenHit,
        ),
    ):
        info = enriched_hit.additional_info.dict(exclude_unset=True, exclude_none=None)
        combined_info = info | additional_info
        enriched_hit.additional_info = models.AdditionalInfo(**combined_info)
    else:
        raise NotImplementedError(
            f"Additional info not supported for hit type: {type(enriched_hit)}"
        )
    triggered_details.hits.append(enriched_hit)

    # if "additional_info" not in triggered_details[hit_time]:
    #     triggered_details[hit_time]["additional_info"] = {}
    # for k, v in additional_info.items():
    #     if k in list(triggered_details[hit_time]["additional_info"].keys()):
    #         triggered_details[hit_time]["additional_info"][k].update(v)
    #     else:
    #         reveal_type(triggered_details[hit_time]["additional_info"][k])
    #         triggered_details[hit_time]["additional_info"][k] = v

    DB.get_db().hset(
        KEY_CANARYDROP + canarytoken.value(),
        "triggered_list",
        json.dumps(triggered_details.serialize_for_v2()),
    )
    data = DB.get_db().hgetall(KEY_CANARYDROP + canarytoken.value())
    print(data)


def get_geoinfo(ip):
    if is_ip_cached(ip):
        return get_geoinfo_from_cache(ip)
    else:
        try:
            resp = get_geoinfo_from_ip(ip)
            add_ip_to_cache(ip, resp)
            return resp
        except Exception as e:  # pragma: no cover
            log.warn("Error getting geo ip: {err}".format(err=e))
            return ""


def get_geoinfo_from_ip(
    ip: str,
    ip_info_api_key: Optional[str] = None,
) -> Dict[str, str]:
    try:
        # This should be async
        resp = requests.get(
            "http://ipinfo.io/" + ip + "/json",
            auth=(ip_info_api_key, "") if ip_info_api_key else None,
            timeout=(3, 3),
        )
        resp.raise_for_status()
        info = resp.json()
    except requests.exceptions.HTTPError as e:
        log.error("ip info error: {e}", e)
        # not strictly Bogon , we have no info
        info = models.GeoIPBogonInfo(ip=ip, bogon=True).dict()
    return info


def get_geoinfo_from_cache(ip):
    key = KEY_CANARY_IP_CACHE + ip
    return json.loads(DB.get_db().get(key))


def is_ip_cached(ip):
    key = KEY_CANARY_IP_CACHE + ip
    check = DB.get_db().exists(key)
    if check == 1:
        return True
    return False


def add_ip_to_cache(ip, geoinfo, exp_time=60 * 60 * 24):
    """Adds an IP with Geo Data to redis.
    Arguments:
    exp_time -- Expiry time for this IP (in seconds). Default set to 1 day.
    """
    key = KEY_CANARY_IP_CACHE + ip
    DB.get_db().setex(key, exp_time, json.dumps(geoinfo))


def add_return_for_token(value: Literal["fortune", "gif"]):
    """Sets`fortune` or `gif` taken from settings"""
    DB.get_db().set(KEY_CANARY_RETURN_TOKEN, value)


def get_return_for_token():
    """Grabs `fortune` or `gif` as set in settings"""
    return DB.get_db().get(KEY_CANARY_RETURN_TOKEN) or "fortune"


# def get_canarydrops(min_time="-inf", max_time="+inf"):
#     """Return a list of stored Canarydrops.
#     Arguments:
#     min_time -- Limit to Canarydrops created after min_time. Format is Unix
#                 epoch. Default is no limit.
#     max_time -- Limit to Canarydrops created before max_time. Format is Unix
#                 epoch. Default is no limit.
#     """
#     canarydrops = []
#     for canarytoken in DB.get_db().zrangebyscore(
#         KEY_CANARYDROPS_TIMELINE,
#         min_time,
#         max_time,
#     ):
#         canarydrops.append(Canarydrop(**get_canarydrop(canarytoken=canarytoken)))
#     return canarydrops


# def get_canarydrops_array(min_time="-inf", max_time="+inf"):
#     """Return an array of stored Canarydrops.
#     Arguments:
#     min_time -- Limit to Canarydrops created after min_time. Format is Unix
#                 epoch. Default is no limit.
#     max_time -- Limit to Canarydrops created before max_time. Format is Unix
#                 epoch. Default is no limit.
#     """
#     canarydrops = []
#     for canarytoken in DB.get_db().zrangebyscore(
#         KEY_CANARYDROPS_TIMELINE,
#         min_time,
#         max_time,
#     ):
#         canarydrops.append(get_canarydrop(canarytoken=canarytoken))
#     return canarydrops


# def load_user(username):
#     """Return a User object.
#     Arguments:
#     username -- A username.
#     """
#     account_key = KEY_USER_ACCOUNT + username
#     if not DB.get_db().exists(account_key):
#         return None

#     from users import User

#     return User(DB.get_db().hgetall(account_key))

# TODO: add counter's / metrics so it's easy to consume.
def lookup_canarytoken_alert_count(canarytoken: tokens.Canarytoken) -> int:
    key = KEY_CANARYTOKEN_ALERT_COUNT + canarytoken.value()
    alert_count = DB.get_db().get(key)
    if alert_count is None:
        return 0
    else:
        return int(alert_count)


def save_canarytoken_alert_count(
    canarytoken: tokens.Canarytoken, count: int, expiry: int
):
    key = KEY_CANARYTOKEN_ALERT_COUNT + canarytoken.value()
    DB.get_db().setex(key, expiry, count)


def do_accounting(canarydrop: cand.Canarydrop, alert_expiry: int):
    """Increments the alert_count for a canarydrop and sets
    it's expiry to `alert_expiry`

    Args:
        canarydrop (cand.Canarydrop): Canarydrop for which alert count is altered.
    """
    alert_count = lookup_canarytoken_alert_count(canarydrop.canarytoken)
    alert_count_incremented = alert_count + 1
    save_canarytoken_alert_count(
        canarydrop.canarytoken, alert_count_incremented, alert_expiry
    )


def can_send_alert(canarydrop: cand.Canarydrop, alert_limit: int = 60):
    alert_count = lookup_canarytoken_alert_count(canarydrop.canarytoken)
    return alert_count < alert_limit


# def save_clonedsite_token(clonedsite_token):
#     if not clonedsite_token.get("canarytoken"):
#         raise Exception("Cannot save an imgur token without a canarydrop")

#     key = (
#         KEY_CLONEDSITE_TOKEN
#         + clonedsite_token["clonedsite"]
#         + ":"
#         + clonedsite_token["canarytoken"]
#     )
#     DB.get_db().hmset(key, clonedsite_token)
#     DB.get_db().sadd(KEY_CLONEDSITE_TOKENS, key)
#     return key


# def get_imgur_count(imgur_id=None):
#     resp = requests.get(
#         "http://imgur.com/ajax/views?images={imgur_id}".format(imgur_id=imgur_id),
#     )
#     resp = resp.json()
#     if not resp["success"] or resp["status"] != 200:
#         raise Exception("Imgur response was unexpected: {resp}".format(resp=resp))
#     return resp["data"][imgur_id]
def add_mail_to_send_status(
    recipient: EmailStr, details: models.TokenAlertDetails
) -> int:
    data = {"recipient": recipient, **details.json_safe_dict()}
    mail_to_send = json.dumps(data)
    return DB.get_db().set(
        f"{KEY_MAIL_TO_SEND}:{details.token}:{details.time.timestamp()}", mail_to_send
    )


def get_all_mails_in_send_status(
    token: str,
) -> list[tuple[list[EmailStr], models.TokenAlertDetails]]:
    mails_and_details = []
    for key in DB.get_db().scan_iter(f"{KEY_MAIL_TO_SEND}:{token}:*"):
        item = DB.get_db().get(key)
        data = json.loads(item)
        recipient = EmailStr(data.pop("recipient"))
        mails_and_details.append((recipient, models.TokenAlertDetails(**data)))
    return mails_and_details


def remove_mail_from_to_send_status(
    token: str, time: datetime.datetime
) -> tuple[Optional[list[EmailStr]], Optional[models.TokenAlertDetails]]:
    item = DB.get_db().getdel(f"{KEY_MAIL_TO_SEND}:{token}:{time.timestamp()}")
    if item is None:
        log.info(f"No mail at key: {KEY_MAIL_TO_SEND}:{token}:{time.timestamp()}")
        return None, None
    data = json.loads(item)
    recipient = EmailStr(data.pop("recipient"))
    return recipient, models.TokenAlertDetails(**data)


def put_mail_on_sent_queue(mail_key: str, details: models.TokenAlertDetails) -> int:
    sent_mail = json.dumps({"mail_key": mail_key, **details.json_safe_dict()})
    return DB.get_db().lpush(KEY_SENT_MAIL_QUEUE, sent_mail)


def pop_mail_off_sent_queue() -> tuple[
    Optional[str], Optional[models.TokenAlertDetails]
]:
    item = DB.get_db().rpop(KEY_SENT_MAIL_QUEUE, count=1)
    if item is None:
        log.info(f"No mail to send on queue: {KEY_SENT_MAIL_QUEUE}")
        return None, None

    data = json.loads(item[0])
    mail_key = data.pop("mail_key")
    return mail_key, models.TokenAlertDetails(**data)


def add_canary_google_api_key(key: str) -> int:
    return DB.get_db().set(KEY_CANARY_GOOGLE_API_KEY, key)


# def save_imgur_token(imgur_token):
#     if not imgur_token.get("canarytoken"):
#         raise Exception("Cannot save an imgur token without a canarydrop")

#     if not imgur_token.get("count", None):
#         imgur_token["count"] = get_imgur_count(imgur_id=imgur_token["id"])

#     key = KEY_IMGUR_TOKEN + imgur_token["id"]
#     DB.get_db().hmset(key, imgur_token)
#     DB.get_db().sadd(KEY_IMGUR_TOKENS, key)
#     return key


# def get_all_imgur_tokens():
#     all_imgur_tokens = []
#     for key in DB.get_db().smembers(KEY_IMGUR_TOKENS):
#         all_imgur_tokens.append(DB.get_db().hgetall(key))
#         all_imgur_tokens[-1]["count"] = int(all_imgur_tokens[-1]["count"])
#     return all_imgur_tokens


# TODO: Doesn't touch redis - remove
# def get_linkedin_viewer_count(username=None, password=None):
#     from twill import get_browser
#     from twill.commands import add_extra_header, fv, go, reset_browser, submit

#     reset_browser()
#     from twill.errors import TwillException

#     add_extra_header(
#         "User-Agent",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36",
#     )
#     go("https://www.linkedin.com/nhome/")
#     # Added because LinkedIn login page no longer names the login form.
#     b = get_browser()
#     form_num = ""
#     for n, f in enumerate(b.get_all_forms()):
#         try:
#             b.get_form_field(f, "session_key")
#             b.get_form_field(f, "session_password")
#             form_num = str(n + 1)
#         except TwillException:
#             pass
#     if form_num == "":
#         log.error("Failed to parse LinkedIn login page - page format may have changed.")
#         raise LinkedInFailure()
#     # fv("login", 'session_password', 'LetsTryPrime')
#     # fv("login", 'session_key', 'ms_DerrickWortham@endian.co.za')
#     fv(form_num, "session_key", username)
#     fv(form_num, "session_password", password)
#     submit()
#     go("http://www.linkedin.com/wvmx/profile?trk=nav_responsive_sub_nav_wvmp")

#     try:
#         for i in (
#             get_browser()
#             .result.lxml.get_element_by_id("viewers_list-content")
#             .iterchildren()
#         ):
#             user_listing = json.loads(i.text.replace("\\u002d", "-"))
#     except Exception as e:
#         log.error("Failed to extract user_listing from page: {error}".format(error=e))
#         raise LinkedInFailure()

#     try:
#         current_count = user_listing["content"]["wvmx_profile_viewers"]["viewersCount"]
#         return current_count
#     except KeyError:
#         log.error(
#             "Profile view struct in unknown format: {user_listing}".format(
#                 user_listing=user_listing,
#             ),
#         )
#         raise LinkedInFailure()


# def get_linkedin_account(username_key=None, username=None):
#     if username:
#         username_key = KEY_LINKEDIN_ACCOUNT + username

#     data = DB.get_db().hgetall(username_key)
#     try:
#         data["count"] = int(data["count"])
#     except KeyError:
#         data["count"] = -1
#     return data


# def get_all_linkedin_accounts():
#     all_linkedin_accounts = []
#     for key in DB.get_db().smembers(KEY_LINKEDIN_ACCOUNTS):
#         all_linkedin_accounts.append(get_linkedin_account(username_key=key))
#     return all_linkedin_accounts


# def create_linkedin_account(username=None, password=None, canarydrop=None):

#     key = KEY_LINKEDIN_ACCOUNT + username

#     if DB.get_db().exists(key):
#         raise KeyError

#     if not canarydrop:
#         from canarytokens.canarydrop import Canarydrop
#         from canarytokens.tokens import Canarytoken

#         ht = Canarytoken()
#         canarydrop = Canarydrop(canarytoken=ht.value())
#     else:
#         ht = canarydrop.canarytoken

#     canarydrop["linkedin_username"] = username
#     save_canarydrop(canarydrop=canarydrop)

#     linkedin_account = {
#         "username": username.lower(),
#         "password": password,
#         "canarytoken": ht.value(),
#         "count": get_linkedin_viewer_count(username=username, password=password),
#     }

#     return save_linkedin_account(linkedin_account=linkedin_account)


# def save_linkedin_account(linkedin_account=None):
#     if not linkedin_account.get("canarytoken"):
#         raise Exception("Cannot save an LinkedIn account without a canarydrop")

#     key = KEY_LINKEDIN_ACCOUNT + linkedin_account["username"]
#     DB.get_db().hmset(key, linkedin_account)
#     DB.get_db().sadd(KEY_LINKEDIN_ACCOUNTS, key)
#     return key


# def get_bitcoin_account(address_key=None, address=None):
#     if address:
#         address_key = KEY_BITCOIN_ACCOUNT + address

#     data = DB.get_db().hgetall(address_key)
#     try:
#         data["balance"] = int(data["balance"])
#     except KeyError:
#         data["balance"] = -1
#     return data


# def get_all_bitcoin_accounts():
#     all_bitcoin_accounts = []
#     for key in DB.get_db().smembers(KEY_BITCOIN_ACCOUNTS):
#         all_bitcoin_accounts.append(get_bitcoin_account(address_key=key))
#     return all_bitcoin_accounts


# def get_bitcoin_address_balance(address=None):
#     resp = requests.get(
#         "https://blockchain.info/q/addressbalance/{address}".format(address=address),
#     )

#     if resp.status_code != 200:
#         raise Exception("Bitcoin response was unexpected: {resp}".format(resp=resp))
#     try:
#         return int(resp.content)
#     except ValueError:
#         raise Exception("Bitcoin response was unexpected: {resp}".format(resp=resp))


# def create_bitcoin_account(address=None, canarydrop=None):

#     key = KEY_BITCOIN_ACCOUNT + address

#     if DB.get_db().exists(key):
#         raise KeyError

#     if not canarydrop:
#         from canarytokens.canarydrop import Canarydrop
#         from canarytokens.tokens import Canarytoken

#         ht = Canarytoken()
#         canarydrop = Canarydrop(canarytoken=ht.value())
#     else:
#         ht = canarydrop.canarytoken

#     canarydrop["bitcoin_account"] = address
#     save_canarydrop(canarydrop=canarydrop)

#     bitcoin_account = {
#         "canarytoken": ht.value(),
#         "address": address,
#         "balance": get_bitcoin_address_balance(address=address),
#     }

#     return save_bitcoin_account(bitcoin_account=bitcoin_account)


# def save_bitcoin_account(bitcoin_account=None):
#     if not bitcoin_account.get("canarytoken"):
#         raise Exception("Cannot save an Bitcoin account without a canarydrop")

#     key = KEY_BITCOIN_ACCOUNT + bitcoin_account["address"]
#     DB.get_db().hmset(key, bitcoin_account)
#     DB.get_db().sadd(KEY_BITCOIN_ACCOUNTS, key)
#     return key


def validate_webhook(url, token_type: models.TokenTypes):
    """Tests if a webhook is valid by sending a test payload
    Arguments:
    url -- Webhook url
    """
    slack = "https://hooks.slack.com"
    payload: Union[models.TokenAlertDetails, models.TokenAlertDetailsSlack]
    if slack in url:
        payload = models.TokenAlertDetailsSlack(
            attachments=[
                models.SlackAttachment(
                    title_link=HttpUrl("https://test.com/check", scheme="https"),
                    fields=[
                        models.SlackField(
                            title="test",
                            value="Working",
                        )
                    ],
                )
            ]
        )
    else:
        payload = models.TokenAlertDetails(
            manage_url=HttpUrl(
                "http://example.com/test/url/for/webhook", scheme="http"
            ),
            channel="HTTP",
            memo=models.Memo("Congrats! The newly saved webhook works"),
            token="a+test+token",
            token_type=token_type,
            src_ip="127.0.0.1",
            additional_data={
                "src_ip": "1.1.1.1",
                "useragent": "Mozilla/5.0...",
                "referer": "http://example.com/referrer",
                "location": "http://example.com/location",
            },
            time=datetime.datetime.now(),
        )
    response = requests.post(
        url,
        payload.json(),
        headers={"content-type": "application/json"},
        timeout=10,
    )
    # TODO: this accepts 3xx which is probably too leanient. We probably want any 2xx code.
    response.raise_for_status()
    # return True
    # except requests.exceptions.Timeout as e:
    #     log.error("Timed out sending test payload to webhook: {url}".format(url=url))
    #     return False
    # except requests.exceptions.RequestException as e:
    #     log.error(
    #         "Failed sending test payload to webhook: {url} with error {error}".format(
    #             url=url,
    #             error=e,
    #         ),
    #     )
    #     return False


def is_tor_relay(ip):

    if not DB.get_db().exists(KEY_TOR_EXIT_NODES):
        update_tor_exit_nodes_loop()  # FIXME: DESIGN: we call defered and expect a result in redis, Now!
    return DB.get_db().sismember(KEY_TOR_EXIT_NODES, json.dumps(ip))


# def update_tor_exit_nodes(contents):
#     if "ExitAddress" in contents:
#         DB.get_db().delete(KEY_TOR_EXIT_NODES)
#     for line in contents.splitlines():
#         if "ExitAddress" in line:
#             DB.get_db().sadd(KEY_TOR_EXIT_NODES, json.dumps(line.split(" ")[1]))


def update_tor_exit_nodes_loop():
    # This breaks tests as it's an uncontrolled side effect
    return
    # d = getPage(b"https://check.torproject.org/exit-addresses")
    # d.addCallback(update_tor_exit_nodes)


def get_certificate(key) -> models.KubeCerts:
    certificate = DB.get_db().hgetall("{}{}".format(KEY_KUBECONFIG_CERTS, key))
    if not certificate:
        raise LookupError(f"{key=} certificate not found in redis.")

    # base64.b64decode(ca.get("c").encode("ascii"))
    return models.KubeCerts(
        k=base64.b64decode(certificate["k"].encode("ascii")),
        c=base64.b64decode(certificate["c"].encode("ascii")),
        f=certificate["f"],
    )


def save_certificate(key, cert_obj: models.KubeCerts):
    """Saves the cert and key as base64 and the digest as given."""
    DB.get_db().hset(
        "{}{}".format(KEY_KUBECONFIG_CERTS, key),
        mapping={
            "c": base64.b64encode(cert_obj["c"]),
            "k": base64.b64encode(cert_obj["k"]),
            "f": cert_obj["f"],
        },
    )


def save_kc_endpoint(ip: IPv4Address, port: models.Port):
    """Save IPv4Address and port for kubeconfig service"""
    DB.get_db().set(KEY_KUBECONFIG_SERVEREP, f"{ip}:{port}")


def get_kc_endpoint() -> Tuple[Optional[IPv4Address], Optional[models.Port]]:
    endpoint = DB.get_db().get(KEY_KUBECONFIG_SERVEREP)
    if endpoint is None:
        return None, None
    ip, port = endpoint.split(":")
    return IPv4Address(ip), models.Port(port)


# def save_kc_hit_for_aggregation(key, hits, update=False):
#     hit_key = "{}{}".format(KEY_KUBECONFIG_HITS, key)
#     DB.get_db().hset(hit_key, "hits", hits)

#     if not update:
#         # typical timeout sent with each kubectl caching discovery request is 32s, and 5 requests are sent as part of each kubectl execution
#         DB.get_db().expire(hit_key, 5 * 32)


# def get_kc_hits(key):
#     return (
#         DB.get_db().hgetall("{}{}".format(KEY_KUBECONFIG_HITS, key)),
#         DB.get_db().pttl("{}{}".format(KEY_KUBECONFIG_HITS, key)),
#     )


def wireguard_keymap_add(public_key: bytes, canarytoken: str) -> None:
    DB.get_db().hset(KEY_WIREGUARD_KEYMAP, public_key, canarytoken)


def wireguard_keymap_del(public_key: bytes) -> None:
    DB.get_db().hdel(KEY_WIREGUARD_KEYMAP, public_key)


def wireguard_keymap_get(public_key: bytes) -> Optional[str]:
    return DB.get_db().hget(KEY_WIREGUARD_KEYMAP, public_key)
