from datetime import datetime

import pytest
from pydantic import EmailStr

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.exceptions import CanarydropAuthFailure, NoCanarytokenPresent
from canarytokens.models import (
    AdditionalInfo,
    DNSTokenHit,
    GeoIPBogonInfo,
    KubeconfigTokenHit,
    Memo,
    TokenTypes,
)
from canarytokens.queries import (
    add_canarydrop_hit,
    add_webhook_token_idx,
    delete_webhook_tokens,
    get_canarydrop,
    get_canarydrop_from_auth,
    save_canarydrop,
)
from canarytokens.tokens import Canarytoken
from tests.utils import make_token_alert_detail


def test_add_delete_webhook(setup_db):
    token_value = Canarytoken.generate()
    webhook_url = "https://hooks.slack.com/test"
    ret = add_webhook_token_idx(webhook_url, canarytoken=token_value)
    assert ret == 1
    delete_webhook_tokens(webhook=webhook_url)


def test_add_hit_get_canarytoken(setup_db):
    canarytoken = Canarytoken()

    canarydrop = Canarydrop(
        generate=True,
        type=TokenTypes.DNS,
        alert_email_enabled=True,
        alert_email_recipient="test@test.com",
        alert_webhook_enabled=True,
        alert_webhook_url="https://hooks.slack.com/test",
        canarytoken=canarytoken,
        memo="stuff happened",
        browser_scanner_enabled=False,
    )
    #
    save_canarydrop(canarydrop)
    token_hit = DNSTokenHit(
        token_type=canarydrop.type,
        time_of_hit=datetime.utcnow().strftime("%s.%f"),
        src_ip="127.0.0.1",
        geo_info=GeoIPBogonInfo(ip="127.0.0.1", bogon=True),
        is_tor_relay=False,
        input_channel="dns",
    )
    add_canarydrop_hit(token_hit=token_hit, canarytoken=canarytoken)
    cd = get_canarydrop(canarytoken=canarytoken)
    assert cd.triggered_details


def test_add_hit_get_canarytoken_wrong_type(setup_db):
    canarytoken = Canarytoken()

    canarydrop = Canarydrop(
        generate=True,
        type=TokenTypes.DNS,
        alert_email_enabled=True,
        alert_email_recipient="test@test.com",
        alert_webhook_enabled=True,
        alert_webhook_url="https://hooks.slack.com/test",
        canarytoken=canarytoken,
        memo="stuff happened",
        browser_scanner_enabled=False,
    )
    #
    save_canarydrop(canarydrop)
    token_hit = KubeconfigTokenHit(
        token_type=TokenTypes.KUBECONFIG,
        time_of_hit=datetime.utcnow().strftime("%s.%f"),
        src_ip="127.0.0.1",
        geo_info=GeoIPBogonInfo(ip="127.0.0.1", bogon=True),
        is_tor_relay=False,
        input_channel="dns",
        additional_info=AdditionalInfo(),
        location="/get",
        useragent="Unknown",
    )
    with pytest.raises(ValueError):
        add_canarydrop_hit(token_hit=token_hit, canarytoken=canarytoken)
    cd = get_canarydrop(canarytoken=canarytoken)
    assert cd.triggered_details


def test_remove_tokens_with_email_x(setup_db):
    """
    There is a 1 to many mapping of email to tokens.
    When requested we need to purge all tokens associated with
    a particular email. This tests the creation and purging of a token
    by email idx.
    """
    email = "test@test.com"
    canarytoken = Canarytoken()
    canarydrop = Canarydrop(
        generate=True,
        type=TokenTypes.DNS,
        alert_email_enabled=True,
        alert_email_recipient=email,
        alert_webhook_enabled=True,
        alert_webhook_url="https://hooks.slack.com/test",
        canarytoken=canarytoken,
        memo="stuff happened",
        browser_scanner_enabled=False,
    )
    save_canarydrop(canarydrop)

    # Check that the toke exists
    cd = get_canarydrop(canarytoken=canarytoken)
    tokens_linked_to_email = queries.list_email_tokens(email_address=email)

    assert cd.alert_email_enabled
    assert cd.alert_email_recipient == EmailStr(email)
    assert len(tokens_linked_to_email)

    # Act. Delete the token using an email
    queries.delete_email_tokens(email_address=email)

    # Check that token has been removed.
    with pytest.raises(NoCanarytokenPresent):
        cd = get_canarydrop(canarytoken=canarytoken)

    tokens_linked_to_email = queries.list_email_tokens(email_address=email)
    assert len(tokens_linked_to_email) == 0


def test_remove_tokens_with_webhook_x():
    """
    There is a 1 to many mapping of webhook to tokens.
    When requested we need to purge all tokens associated with
    a particular webhook. This tests the creation and purging of a token
    by webhook idx.
    """
    webhook = "https://hooks.slack.com/test"

    canarytoken = Canarytoken()
    canarydrop = Canarydrop(
        generate=True,
        type=TokenTypes.DNS,
        alert_email_enabled=True,
        alert_email_recipient="test@test.com",
        alert_webhook_enabled=True,
        alert_webhook_url=webhook,
        canarytoken=canarytoken,
        memo="stuff happened",
        browser_scanner_enabled=False,
    )
    save_canarydrop(canarydrop)

    # Check that the toke exists
    cd = get_canarydrop(canarytoken=canarytoken)
    tokens_linked_to_webhook = queries.list_webhook_tokens(webhook=webhook)

    assert cd.alert_webhook_enabled
    assert cd.alert_webhook_url == webhook
    assert len(tokens_linked_to_webhook)

    # Act. Delete the token using an webhook
    queries.delete_webhook_tokens(webhook=webhook)

    # Check that token has been removed.
    with pytest.raises(NoCanarytokenPresent):
        cd = get_canarydrop(canarytoken=canarytoken)
    tokens_linked_to_webhook = queries.list_webhook_tokens(webhook=webhook)
    assert len(tokens_linked_to_webhook) == 0


def test_get_canarydrop_from_auth(setup_db):
    webhook = "https://hooks.slack.com/test"

    canarytoken = Canarytoken()
    canarydrop = Canarydrop(
        generate=True,
        type=TokenTypes.DNS,
        alert_email_enabled=True,
        alert_email_recipient="test@test.com",
        alert_webhook_enabled=True,
        alert_webhook_url=webhook,
        canarytoken=canarytoken,
        memo="stuff happened",
        browser_scanner_enabled=False,
    )
    save_canarydrop(canarydrop)
    new_drop = get_canarydrop_from_auth(
        token=canarydrop.canarytoken.value(), auth=canarydrop.auth
    )
    assert new_drop.canarytoken.value() == canarydrop.canarytoken.value()

    with pytest.raises(CanarydropAuthFailure):
        get_canarydrop_from_auth(
            token=canarydrop.canarytoken.value(), auth="wrongauthtoken"
        )


def test_get_geoinfo_is_cached():
    """
    IP's are enriched with geo info. A 3rd party service is
    used to provide this.
    This test ensures we cache and evict this info correctly.
    We don't want to fetch too often but we don't want stale data either.

    TODO:   Check we evicte cache based on time. unittest.mock
            to modify the date and check we empty the cache and re-fetch
    """
    ip = "166.73.125.172"
    assert not queries.is_ip_cached(ip)
    geoinfo = queries.get_geoinfo(ip)
    geoinfo_cache = queries.get_geoinfo_from_cache(ip)
    assert geoinfo == geoinfo_cache

    # Check cache path is hit
    assert queries.is_ip_cached(ip)
    geoinfo = queries.get_geoinfo(ip)
    geoinfo_cache = queries.get_geoinfo_from_cache(ip)
    assert geoinfo == geoinfo_cache
    # TODO:   Check we evicte cache based on time. unittest.mock
    # to modify the date and check we empty the cache and re-fetch


def test_mail_queue(setup_db):
    details = make_token_alert_detail()
    mail_key = "some_unique_key"
    queries.put_mail_on_sent_queue(
        mail_key=mail_key,
        details=details,
    )
    got_mail_key, got_details = queries.pop_mail_off_sent_queue()
    assert got_mail_key == mail_key
    assert got_details.json() == details.json()

    got_mail_key, got_details = queries.pop_mail_off_sent_queue()
    assert got_mail_key is None
    assert got_details is None


def test_add_pop_mail_queue(setup_db):
    details = make_token_alert_detail()
    mail_key = "some_unique_key"

    queries.put_mail_on_sent_queue(
        mail_key=mail_key,
        details=details,
    )
    got_mail_key, got_details = queries.pop_mail_off_sent_queue()
    assert got_mail_key == mail_key
    assert got_details.json() == details.json()

    got_mail_key, got_details = queries.pop_mail_off_sent_queue()
    assert got_mail_key is None
    assert got_details is None


def test_add_many_pop_many_mail_queue(setup_db):
    details_1 = make_token_alert_detail(memo=Memo("message 1"))
    mail_key_1 = "some_unique_key_1"

    queries.put_mail_on_sent_queue(
        mail_key=mail_key_1,
        details=details_1,
    )

    details_2 = make_token_alert_detail(memo=Memo("message 2"))
    mail_key_2 = "some_unique_key_2"

    queries.put_mail_on_sent_queue(
        mail_key=mail_key_2,
        details=details_2,
    )

    got_mail_key, got_details = queries.pop_mail_off_sent_queue()
    assert got_mail_key == mail_key_1
    assert got_details.json() == details_1.json()

    got_mail_key, got_details = queries.pop_mail_off_sent_queue()
    assert got_mail_key == mail_key_2
    assert got_details.json() == details_2.json()


def test_add_mail_to_send_status(setup_db):
    recipient = EmailStr("help@test,com")
    details = make_token_alert_detail(memo=Memo("message 2"))
    queries.add_mail_to_send_status(
        recipient=recipient,
        details=details,
    )
    got_recipient, got_details = queries.remove_mail_from_to_send_status(
        token=details.token,
        time=details.time,
    )
    assert got_recipient == recipient
    assert got_details.json() == details.json()


def test_add_add_get_return_for_token(setup_db):
    assert queries.get_return_for_token() == "fortune"
    queries.add_return_for_token("gif")
    assert queries.get_return_for_token() == "gif"
