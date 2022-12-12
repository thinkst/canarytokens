#!/usr/bin/env python3

import json, os, sys
from cctoken import CreditCard
from extendtoken import ExtendAPI

def gen_cc_token(url : str) -> None:
    '''Generates a CC token using the passed URL callback'''
    username = os.environ.get('CANARY_EXTEND_USERNAME', '')
    password = os.environ.get('CANARY_EXTEND_PASSWORD', '')
    #eapi = ExtendAPI(username, password)
    #cc = eapi.create_credit_card(metadata=url)
    cc = CreditCard('123', 'Harold Boyd', '0000 1234 12334242', '1234', expiration='12/23', kind='AMEX', billing_zip='05089')
    out = {
        'rendered_html': cc.render_html(),
        'number': cc.number,
        'csv': cc.to_csv()
    }
    print(json.dumps(out))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        gen_cc_token(sys.argv[1])
    else:
        print('')