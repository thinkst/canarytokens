#!/usr/bin/env python3

import json, os, sys
from cctoken import CreditCard
from extendtoken import ExtendAPI

def gen_cc_token(url : str) -> None:
    '''Generates a CC token using the passed URL callback'''
    username = os.environ.get('CANARY_EXTEND_USERNAME', '')
    password = os.environ.get('CANARY_EXTEND_PASSWORD', '')

    # Just so it returns something...
    cc = CreditCard('123', 'Harold Boyd', '370021994416137', '123', expiration='12/23', kind='AMEX', billing_zip='05089')

    eapi = ExtendAPI(username, password)
    cc = eapi.create_credit_card(metadata=url)
    out = {
        'rendered_html': cc.render_html(),
        'expiration': cc.expiration,
        'number': cc.number,
        'cvc': cc.cvc,
        'csv': cc.to_csv()
    }
    print(json.dumps(out))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        gen_cc_token(sys.argv[1])
    else:
        print('')