#!/usr/bin/env python3

# Functionality for an Extend-based CC canarytoken
# (C) 2022 Thinkst Labs

from os import environ
import os.path
from cctoken import CreditCard
import requests, datetime, time
from datagen import generate_person
from typing import List, Optional, Tuple, Dict

class ExtendAPI(object):
    '''Class for interacting with the Extend API for virtual card management'''
    def __init__(self, email = environ.get('EXTEND_EMAIL', ''), password = environ.get('EXTEND_PASSWORD', ''), token = None):
        self.email = email
        self.token = token
        self.kind = 'AMEX'
        if self.token:
            return

        req = self._post_api('https://api.paywithextend.com/signin', {'email': self.email, 'password': password})
        if req.status_code == 200 and req.json().get('error', '') == '':
            print(req.json())
            self.token = req.json().get('token')
            self.refresh_token = req.json().get('refresh_token')
        else:
            print(req.json())
    
    def _post_api(self, endpoint , data=None):
        '''Performs a POST against the passed endpoint with the data passed'''
        headers = {'Content-Type': 'application/json', 'Accept': 'application/vnd.paywithextend.v2021-03-12+json'}
        if self.token != None:
            headers['Authorization'] = 'Bearer {}'.format(self.token)
        return requests.post(endpoint, json=data, headers=headers)
    
    #def g(self, endpoint, data = None):
    #    return self._get_api(endpoint=endpoint, data=data)

    def _get_api(self, endpoint, data=None):
        '''Performs a GET against the passed endpoint'''
        headers = {'Content-Type': 'application/json', 'Accept': 'application/vnd.paywithextend.v2021-03-12+json'}
        if self.token != None:
            headers['Authorization'] = 'Bearer {}'.format(self.token)
        return requests.get(endpoint, headers=headers, json=data)
    
    def _put_api(self, endpoint, data=None):
        '''Performs a PUT against the passed endpoint'''
        headers = {'Content-Type': 'application/json', 'Accept': 'application/vnd.paywithextend.v2021-03-12+json'}
        if self.token != None:
            headers['Authorization'] = 'Bearer {}'.format(self.token)
        return requests.put(endpoint, headers=headers, json=data)

    def _delete_api(self, endpoint):
        '''Performs a DELETE against the passed endpoint'''
        headers = {'Content-Type': 'application/json', 'Accept': 'application/vnd.paywithextend.v2021-03-12+json'}
        if self.token:
            headers['Authorization'] = 'Bearer {}'.format(self.token)
        return requests.delete(endpoint, headers=headers)

    def refresh_auth_token(self):
        '''Refreshes the auth session token'''
        req = self._post_api('https://api.paywithextend.com/renewauth', {'refreshToken': self.refresh_token, 'email': self.email})
        if req.status_code == 200 and req.json().get('error', '') == '':
            self.token = req.json().get('token')
            self.refresh_token = req.json().get('refresh_token')
    
    @classmethod
    def fetch_token(cls, path=None):
        if not path:
            raise Exception("No path supplied")
        
        if not os.path.exists(path):
            raise Exception("File does not exist: {}".format(path))
        
        with open(path) as f:
            return f.read().strip()

    def get_virtual_cards(self):
        '''Returns a list of tuples of (card owner, card id)'''
        req = self._get_api('https://api.paywithextend.com/virtualcards?count=50&page=0')
        cards = []
        if req.status_code == 200 and req.json().get('error', '') == '':
            for vc in req.json().get('virtualCards', []):
                cards.append((vc['recipient']['firstName'] + ' ' + vc['recipient']['lastName'], vc.get('id')))
        else:
            print(req.text)
        return cards
    
    def get_card_info(self, card_id):
        '''Returns all the data about a passed card_id available'''
        req = self._get_api('https://v.paywithextend.com/virtualcards/' + card_id)
        if req.status_code == 200 and req.json().get('error', '') == '':
            return req.json()
        return None
    
    def get_transaction(self, txn_id):
        '''Returns more details about a specific transaction'''
        req = self._get_api('https://api.paywithextend.com/transactions/' + txn_id)
        if req.status_code == 200 and req.json().get('error', '') == '':
            return req.json()
        return None
    
    def get_card_transactions(self, card_id):
        '''Gets all the recent card transactions for a given card_id'''
        req = self._get_api('https://api.paywithextend.com/virtualcards/{0}/transactions?status=DECLINED,PENDING,CLEARED'.format(card_id))
        if req.status_code == 200 and req.json().get('error', '') == '':
            return req.json().get('transactions', [])
    
    def get_latest_transaction(self, cc):
        '''Gets the latest transaction for a given credit card'''
        txns = self.get_card_transactions(cc.id)
        if len(txns) == 0:
            return None
        max_tx = txns[0]
        max_dt = datetime.datetime.fromisoformat(max_tx['authedAt'].split('+')[0])
        for txn in txns:
            dt = datetime.datetime.fromisoformat(txn['authedAt'].split('+')[0])
            if dt > max_dt:
                max_dt = dt
                max_tx = txn
        return {max_dt.toisoformat(): max_tx}

    def get_parent_card_id(self):
        '''Gets the ID of the organization's real CC'''
        req = self._get_api('https://api.paywithextend.com/creditcards', {"count": 1})
        if req.status_code == 200:
            return req.json().get('creditCards')[0]['id']
        return ''

    def make_card(self, first_name, last_name, token_url, limit_cents=100):
        '''Creates a new CreditCard via Extend's CreateVirtualCard API'''
        cc = self.get_parent_card_id()
        now_ts = datetime.datetime.now() - datetime.timedelta(days=1)
        now_ts = now_ts.isoformat() + '+0000'
        expiry = datetime.datetime.now() + datetime.timedelta(weeks=52)
        future_ts = expiry.isoformat() + '+0000'
        expiry_str = str(expiry.month) + '/' + str(expiry.year)
        notes = token_url
        data = {
            "creditCardId": cc,
            "recipient": self.email,
            "displayName": first_name + ' ' + last_name + "'s card",
            "balanceCents": limit_cents,
            "direct": "false",
            "recurs": "false",
            "validFrom": now_ts,
            "validTo": future_ts,
            "notes": notes,
            "referenceFields": [],
            "validMccRanges": [{"lowest": "9403", "highest": "9403"}]
        }

        req = self._post_api('https://api.paywithextend.com/virtualcards', data=data)
        out = CreditCard("", first_name + ' ' + last_name, None, None, '', expiry_str, None, kind = self.kind)
        if req.status_code == 200 and req.json().get('error', '') == '':
            out.id = req.json().get('virtualCard')['id']
            vc_info = self.get_card_info(out.id)
            if 'vcn' in vc_info['virtualCard'].keys():
                out.cvc = vc_info['virtualCard']['securityCode']
                out.number = vc_info['virtualCard']['vcn']
                #self.cancel_card(out.id)
            else:
                print("ERROR GETTING CARD DETAILS")
        else:
            print('Error: ' + str(req.json()))
            return None
        return out

    def cancel_card(self, card_id):
        '''Cancels a passed card'''
        req = self._put_api('https://api.paywithextend.com/virtualcards/' + card_id + '/cancel')
        if req.status_code != 200:
            print("Error cancelling: " + card_id)

    def create_credit_card(self, first_name=None, last_name=None, address=None, billing_zip=None, metadata = None):
        '''Creates a cardholder and associated virtual card for the passed person, if not passed, will generate fake data to use'''
        fake_person = generate_person()
        if first_name is None:
            first_name = fake_person['first_name']
        if last_name is None:
            last_name = fake_person['last_name']
        if address is None:
            address = fake_person['address']
        if billing_zip is None:
            billing_zip = fake_person['billing_zip']
        if metadata is None:
            metadata = ''
        cc = self.make_card(first_name, last_name, token_url=metadata)
        if not cc:
            return None
        cc.address = address
        cc.billing_zip = billing_zip
        return cc
    
    def get_credit_card(self, id):
        '''Abstract method to get a virtual credit card'''
        pass
    
    def get_transaction_events(self, since=None):
        '''Returns a list of recent transactions for the org'''
        txns = []
        req = self._get_api('https://api.paywithextend.com/events')
        if req.status_code == 200 and req.json().get('error', '') == '':
            for event in req.json().get('events'):
                if since != None:
                    if since > datetime.datetime.fromisoformat(event['timestamp'].split('+')[0]):
                        # We've gone far enough back to not need to continue
                        return txns
                if 'transaction' in event['type']:
                    txns.append(event['data'])
            if req.json().get('pagination')['numberOfPages'] > 1:
                page = 1
                while page < req.json().get('pagination')['numberOfPages']:
                    req = self._get_api('https://api.paywithextend.com/events?page={0}'.format(str(page)))
                    if req.status_code == 200 and req.json().get('error', '') == '':
                        for event in req.json().get('events'):
                            if since != None:
                                if since > datetime.datetime.fromisoformat(event['timestamp'].split('+')[0]):
                                    # We've gone far enough back to not need to continue
                                    return txns
                            if 'transaction' in event['type']:
                                txns.append(event['data'])
                    else:
                        print("Error fetching further pages of data")
                        return txns
                    page += 1
        return txns

    def subscribe_to_txns(self, url):
        '''Adds a subscription to send transaction events to the passed webhook url'''
        parent_cc = self.get_parent_card_id()
        events = ['transaction.authorized', 'transaction.declined', 'transaction.reversed', 'transaction.settled', 'transaction.updated.no_match']
        body = {
            'creditCardId': parent_cc,
            'enabledEvents': events,
            'url': url
        }
        req = self._post_api('https://api.paywithextend.com/subscriptions', body)
        if req.status_code == 200 and req.json().get('error', '') == '':
            return req.json()
        print("Error: " + str(req.json()))
        return {}

    def delete_subscription(self, sub_id):
        self._delete_api('https://api.paywithextend.com/subscriptions/' + sub_id)

    def get_transaction_info_from_event(self, eventid):
        '''Returns the virtual card ID from a transaction event'''
        res = self._get_api('https://api.paywithextend.com/events/' + eventid)
        if res.status_code != 200 or res.json().get('error', '') != '':
            print("Error retrieving event!")
            return None
        return res.json().get('event', {}).get('data', {})

    def issue_test_transaction(self, cc, amount):
        '''Issues a test transaction to the passed card'''
        return None # This API does not work for "real" cards
        data = {
            'amount': amount,
            'type': 'DECLINED'
        }
        req = self._post_api('https://api.paywithextend.com/virtualcards/{0}/transactions/simulate'.format(cc.id), data=data)
        if req.status_code != 200:
            print("Error issuing test transaction to: " + cc.id)
            return req
