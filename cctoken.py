#!/usr/bin/env python3

# (C) 2022 Thinkst Applied Research
# Base class for implementing a credit card token

from typing import Optional, Dict
from abc import ABCMeta, abstractmethod
from io import StringIO
import csv

class CreditCard(object):
    '''Simple class to represent a credit card and its associated owner information.'''
    def __init__(self, id, name, number, cvc, billing_zip, expiration = None, address = '', kind = None):
        self.id = id
        self.name = name
        self.number = number
        self.billing_zip = billing_zip
        self.expiration = expiration
        self.cvc = cvc
        self.address = address
        self.kind = kind
    
    def render_html(self):
        '''Returns an HTML div to render the card info on a website'''
        return '''<div id="cccontainer" style="position: relative; margin: auto; background-image: url('/resources/cc-background-{kind}.png'); height: 290px; width: 460px;"><span id="ccname" style="left: 45px; top: 135px; font-family: 'Open Sans'; position: absolute; font-size: 20pt; color: white;">{name}</span><span id="ccnumber" style="left: 45px; top: 160px; font-family: 'Open Sans'; position: absolute; font-size: 20pt; color: white; word-spacing: .45em;">{number}</span><span id="ccexpires" style="left: 45px; top: 230px; position: absolute; font-family: 'Open Sans'; font-size: 18pt; color: white;">{expiration}</span><span id="cccvc" style="left: 240px; top: 230px; position: absolute; font-family: 'Open Sans'; font-size: 18pt; color: white;">{cvc}</span></div>'''.format(kind=self.kind, cvc=self.cvc, number=self.number, name=self.name, expiration=self.expiration)

    def to_csv(self):
        f = StringIO()
        fn = ['name', 'type', 'number', 'cvc', 'exp', 'billing_zip']
        sd = self.to_dict()
        del sd['address']
        del sd['id']
        writer = csv.DictWriter(f, fieldnames=fn)
        writer.writeheader()
        writer.writerow(sd)
        return f.getvalue()

    def to_dict(self):
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

# class ApiProvider(metaclass = ABCMeta):
#     '''Abstract base class for a credit card API provider'''
#     def __init__(self):
#         pass
    
#     @abstractmethod
#     def create_credit_card(self, first_name = None, last_name = None, address = None, billing_zip = None):
#         '''Abstract method to create a virtual credit card number'''
#         pass
    
#     @abstractmethod
#     def get_credit_card(self, id):
#         '''Abstract method to get a virtual credit card'''
#         pass

#     @abstractmethod
#     def get_latest_transaction(self, cc : CreditCard):
#         '''Abstract method to get the latest transaction for a credit card'''
#         pass

class CCToken(object):
    def __init__(self, api_provider):
        pass