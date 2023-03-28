import datetime
import json
import os
from typing import Optional

import requests

from canarytokens.datagen import generate_person
from canarytokens.models import ApiProvider, CreditCard


class ExtendAPIException(Exception):
    pass


class ExtendAPIRateLimitException(Exception):
    pass


class ExtendAPICardsException(Exception):
    pass


class ExtendAPI(ApiProvider):
    """Class for interacting with the Extend API for virtual card management"""

    def __init__(
        self,
        email,
        password,
        card_name,
        token=None,
    ):
        self.email = email
        self.token = token
        self.kind = "AMEX"
        self.card_name = card_name
        if self.token:
            return

        req = self._post_api(
            "https://api.paywithextend.com/signin",
            {"email": self.email, "password": password},
        )
        self.token = req.json().get("token")
        self.refresh_token = req.json().get("refresh_token")

    def _post_api(self, endpoint: str, data: Optional[str] = None) -> requests.Response:
        """Performs a POST against the passed endpoint with the data passed"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        }
        if self.token is not None:
            headers["Authorization"] = "Bearer {}".format(self.token)
        resp = requests.post(endpoint, json=data, headers=headers)
        if resp.status_code == 422:
            raise ExtendAPIRateLimitException(
                "ExtendAPI call failed with 422 rate limit."
            )
        print(resp.content)
        try:
            json_error, text_error = resp.json().get("error", ""), ""
        except requests.exceptions.JSONDecodeError:
            json_error, text_error = "", resp.text
        if resp.status_code != 200 or json_error:
            raise ExtendAPIException(
                "ExtendAPI call failed. Response code {}, error={}".format(
                    resp.status_code, repr(json_error + text_error)
                )
            )
        return resp

    def _get_api(
        self, endpoint: str, data: Optional[str] = None
    ) -> requests.Response:  # pragma: no cover
        """Performs a GET against the passed endpoint"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        }
        if self.token is not None:
            headers["Authorization"] = "Bearer {}".format(self.token)
        resp = requests.get(endpoint, headers=headers, json=data)
        if resp.status_code != 200 or resp.json().get("error", "") != "":
            raise ExtendAPIException(
                "ExtendAPI call failed. Response code {}, error={}".format(
                    resp.status_code, resp.json().get("error")
                )
            )
        return resp

    def _put_api(
        self, endpoint: str, data: Optional[str] = None
    ) -> requests.Response:  # pragma: no cover
        """Performs a PUT against the passed endpoint"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        }
        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"
        resp = requests.put(endpoint, headers=headers, json=data)
        if resp.status_code != 200 or resp.json().get("error", "") != "":
            raise ExtendAPIException(
                "ExtendAPI call failed. Response code {}, error={}".format(
                    resp.status_code, resp.json().get("error")
                )
            )
        return resp

    def _delete_api(self, endpoint: str):  # pragma: no cover
        """Performs a DELETE against the passed endpoint"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        resp = requests.delete(endpoint, headers=headers)
        if resp.status_code != 200 or resp.json().get("error", "") != "":
            raise ExtendAPIException(
                "ExtendAPI call failed. Response code {}, error={}".format(
                    resp.status_code, resp.json().get("error")
                )
            )
        return resp

    def _refresh_auth_token(self):  # pragma: no cover
        """Refreshes the auth session token"""
        req = self._post_api(
            "https://api.paywithextend.com/renewauth",
            {"refreshToken": self.refresh_token},
        )
        self.token = req.json().get("token")
        self.refresh_token = req.json().get("refresh_token")

    @classmethod
    def fetch_credentials(cls, path=None):  # pragma: no cover
        if not path:
            raise Exception("No path supplied")

        if not os.path.exists(path):
            raise Exception(f"File does not exist: {path}")

        with open(path) as f:
            credentials = json.loads(f.read().strip())

        return credentials["EXTEND_EMAIL_ADDRESS"], credentials["EXTEND_API_KEY"]

    def get_virtual_cards(self) -> list[tuple[str, str]]:  # pragma: no cover
        """Returns a list of tuples of (card owner, card id)"""
        req = self._get_api(
            "https://api.paywithextend.com/virtualcards?count=50&page=0"
        )
        cards = []
        for vc in req.json().get("virtualCards", []):
            cards.append(
                (
                    vc["recipient"]["firstName"] + " " + vc["recipient"]["lastName"],
                    vc.get("id"),
                )
            )
        return cards

    def get_card_info(self, card_id) -> Optional[dict[str, str]]:
        """Returns all the data about a passed card_id available"""
        req = self._get_api("https://v.paywithextend.com/virtualcards/" + card_id)
        return req.json()

    def get_transaction(
        self, txn_id: str
    ) -> Optional[dict[str, str]]:  # pragma: no cover
        """Returns more details about a specific transaction"""
        req = self._get_api("https://api.paywithextend.com/transactions/" + txn_id)
        return req.json()

    def get_card_transactions(self, card_id) -> list[dict]:  # pragma: no cover
        """Gets all the recent card transactions for a given card_id"""
        req = self._get_api(
            "https://api.paywithextend.com/virtualcards/{0}/transactions?status=DECLINED,PENDING,CLEARED".format(
                card_id
            )
        )
        return req.json().get("transactions", [])

    def get_latest_transaction(
        self, cc: CreditCard
    ) -> Optional[dict[str, str]]:  # pragma: no cover
        """Gets the latest transaction for a given credit card"""
        txns = self.get_card_transactions(cc.id)
        if len(txns) == 0:
            return None
        max_tx = txns[0]
        max_dt = datetime.datetime.fromisoformat(max_tx["authedAt"].split("+")[0])
        for txn in txns:
            dt = datetime.datetime.fromisoformat(txn["authedAt"].split("+")[0])
            if dt > max_dt:
                max_dt = dt
                max_tx = txn
        return {max_dt.toisoformat(): max_tx}

    def get_parent_card_id(self) -> str:  # pragma: no cover
        """Gets the ID of the organization's real CC"""
        resp = self._get_api("https://api.paywithextend.com/creditcards")
        cards = resp.json().get("creditCards")
        # import rpdb; rpdb.set_trace()
        if len(cards) == 0:
            raise ExtendAPICardsException("No cards returned from Extend")

        filtered_cards = [x for x in cards if x["displayName"] == self.card_name]

        if len(filtered_cards) == 0:
            raise ExtendAPICardsException("No card is called {}".format(self.card_name))

        if len(filtered_cards) > 1:
            raise ExtendAPICardsException(
                "Multiple cards are called {}".format(self.card_name)
            )

        return filtered_cards[0]["id"]

    def make_card(
        self,
        token_url: str,
        first_name: str,
        last_name: str,
        address: str,
        billing_zip: str,
        limit_cents: int = 100,
    ) -> CreditCard:
        """Creates a new CreditCard via Extend's CreateVirtualCard API"""
        cc = self.get_parent_card_id()
        now_ts = datetime.datetime.now() - datetime.timedelta(days=1)
        now_ts = now_ts.isoformat() + "+0000"
        expiry = datetime.datetime.now() + datetime.timedelta(weeks=2 * 52)
        future_ts = expiry.isoformat() + "+0000"
        expiry_str = str(expiry.month) + "/" + str(expiry.year)
        notes = token_url
        data = {
            "creditCardId": cc,
            "recipient": self.email,
            "displayName": first_name + " " + last_name + "'s card",
            "balanceCents": limit_cents,
            "direct": "false",
            "recurs": "false",
            "validFrom": now_ts,
            "validTo": future_ts,
            "notes": notes,
            "referenceFields": [],
            "validMccRanges": [{"lowest": "9403", "highest": "9403"}],
        }
        out = CreditCard(
            id="",
            name=first_name + " " + last_name,
            number=None,
            cvc=None,
            billing_zip=billing_zip,
            expiration=expiry_str,
            address=address,
            kind=self.kind,
        )
        req = self._post_api("https://api.paywithextend.com/virtualcards", data=data)
        out.id = req.json().get("virtualCard")["id"]
        vc_info = self.get_card_info(out.id)
        if "vcn" in vc_info["virtualCard"].keys():
            out.cvc = vc_info["virtualCard"]["securityCode"]
            out.number = vc_info["virtualCard"]["vcn"]
        else:
            print("ERROR GETTING CARD DETAILS")
        return out

    def cancel_card(self, card_id) -> None:  # pragma: no cover
        """Cancels a passed card"""
        _ = self._put_api(
            "https://api.paywithextend.com/virtualcards/" + card_id + "/cancel"
        )

    def create_credit_card(
        self,
        token_url: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        address: Optional[str] = None,
        billing_zip: Optional[str] = None,
    ) -> CreditCard:
        """Creates a cardholder and associated virtual card for the passed person, if not passed, will generate fake data to use"""
        fake_person = generate_person()
        if first_name is None:
            first_name = fake_person["first_name"]
        if last_name is None:
            last_name = fake_person["last_name"]
        if address is None:
            address = fake_person["address"]
        if billing_zip is None:
            billing_zip = fake_person["billing_zip"]

        cc = self.make_card(
            token_url=token_url,
            first_name=first_name,
            last_name=last_name,
            address=address,
            billing_zip=billing_zip,
        )

        return cc

    def get_credit_card(self, id: str) -> CreditCard:
        """Abstract method to get a virtual credit card"""
        pass

    def get_transaction_events(  # noqa C901  # pragma: no cover
        self, since: Optional[datetime.datetime] = None
    ) -> list:
        """Returns a list of recent transactions for the org"""
        txns = []
        req = self._get_api("https://api.paywithextend.com/events")
        for event in req.json().get("events"):
            if since is not None:
                if since > datetime.datetime.fromisoformat(
                    event["timestamp"].split("+")[0]
                ):
                    # We've gone far enough back to not need to continue
                    return txns
            if "transaction" in event["type"]:
                txns.append(event["data"])
        if req.json().get("pagination")["numberOfPages"] > 1:
            page = 1
            while page < req.json().get("pagination")["numberOfPages"]:
                req = self._get_api(
                    "https://api.paywithextend.com/events?page={0}".format(str(page))
                )
                for event in req.json().get("events"):
                    if since is not None:
                        if since > datetime.datetime.fromisoformat(
                            event["timestamp"].split("+")[0]
                        ):
                            # We've gone far enough back to not need to continue
                            return txns
                    if "transaction" in event["type"]:
                        txns.append(event["data"])
                page += 1
        return txns

    def subscribe_to_txns(self, url: str):  # pragma: no cover
        """Adds a subscription to send transaction events to the passed webhook url"""
        parent_cc = self.get_parent_card_id()
        events = [
            "transaction.authorized",
            "transaction.declined",
            "transaction.reversed",
            "transaction.settled",
            "transaction.updated.no_match",
        ]
        body = {"creditCardId": parent_cc, "enabledEvents": events, "url": url}
        req = self._post_api("https://api.paywithextend.com/subscriptions", body)
        return req.json()

    def delete_subscription(self, sub_id):  # pragma: no cover
        self._delete_api("https://api.paywithextend.com/subscriptions/" + sub_id)

    def get_transaction_info_from_event(self, eventid: str):  # pragma: no cover
        """Returns the virtual card ID from a transaction event"""
        res = self._get_api("https://api.paywithextend.com/events/" + eventid)
        return res.json().get("event", {}).get("data", {})

    def issue_test_transaction(
        self, cc: CreditCard, amount: int = 1000
    ) -> None:  # pragma: no cover
        """Issues a test transaction to the passed card"""
        return None  # This API does not work for "real" cards
        data = {"amount": amount, "type": "DECLINED"}
        req = self._post_api(
            "https://api.paywithextend.com/virtualcards/{0}/transactions/simulate".format(
                cc.id
            ),
            data=data,
        )
        if req.status_code != 200:
            print("Error issuing test transaction to: " + cc.id)
            return req
