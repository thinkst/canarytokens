#!/usr/bin/env python3

# (C) 2022 Thinkst Applied Research
# Base class for implementing a credit card token

from typing import Optional, Dict
from abc import ABCMeta, abstractmethod
from io import StringIO
import csv

class CreditCard(object):
    '''Simple class to represent a credit card and its associated owner information.'''
    def __init__(self, id, name : str, number : Optional[str], cvc : Optional[str], billing_zip : str, expiration : Optional[str] = None, address : str = '', kind : Optional[str] = None):
        self.id = id
        self.name : str = name
        self.number : Optional[str] = number
        self.billing_zip : str = billing_zip
        self.expiration : Optional[str] = expiration
        self.cvc : Optional[str] = cvc
        self.address : str = address
        self.kind : Optional[str] = kind
    
    def render_html(self) -> str:
        '''Returns an HTML div to render the card info on a website'''
        return '''<div id="cccontainer" style="position: relative; background-image: url('/resources/cc-background-{kind}.png'); height: 290px; width: 460px;"><span id="ccname" style="left: 50px; top: 140px; font-family: 'Open Sans'; position: absolute; font-size: 20pt; color: white;">{name}</span><span id="ccnumber" style="left: 50px; top: 165px; font-family: 'Open Sans'; position: absolute; font-size: 20pt; color: white; word-spacing: .45em;">{number}</span><span id="ccexpires" style="left: 50px; top: 235px; position: absolute; font-family: 'Open Sans'; font-size: 18pt; color: white;">{expiration}</span><span id="cccvc" style="left: 245px; top: 235px; position: absolute; font-family: 'Open Sans'; font-size: 18pt; color: white;">{cvc}</span></div>'''.format(kind=self.kind, cvc=self.cvc, number=self.number, name=self.name, expiration=self.expiration)

    def to_csv(self) -> str:
        f = StringIO()
        fn = ['name', 'type', 'number', 'cvc', 'exp', 'billing_zip']
        sd = self.to_dict()
        del sd['address']
        del sd['id']
        writer = csv.DictWriter(f, fieldnames=fn)
        writer.writeheader()
        writer.writerow(sd)
        return f.getvalue()

    def to_dict(self) -> Dict[str, str]:
        '''Returns the CC information as a python dict'''
        out = {
            'id': str(self.id),
            'name': self.name,
            'number': str(self.number),
            'cvc': str(self.cvc),
            'billing_zip': str(self.billing_zip),
            'type': str(self.kind),
            'address': str(self.address),
            'exp': str(self.expiration)
        }
        return out

class ApiProvider(metaclass = ABCMeta):
    '''Abstract base class for a credit card API provider'''
    def __init__(self):
        pass
    
    @abstractmethod
    def create_credit_card(self, first_name : Optional[str] = None, last_name : Optional[str] = None, address : Optional[str] = None, billing_zip : Optional[str] = None) -> CreditCard:
        '''Abstract method to create a virtual credit card number'''
        pass
    
    @abstractmethod
    def get_credit_card(self, id : str) -> CreditCard:
        '''Abstract method to get a virtual credit card'''
        pass

    @abstractmethod
    def get_latest_transaction(self, cc : CreditCard) -> Optional[Dict[str, str]]:
        '''Abstract method to get the latest transaction for a credit card'''
        pass

class CCToken(object):
    def __init__(self, api_provider : ApiProvider):
        pass

