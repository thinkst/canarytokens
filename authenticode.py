from sign_file import authenticode_sign_binary

import tempfile
from os import unlink

def make_canary_authenticode_binary(hostname=None, filebody=[]):
    unsigned_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    unsigned_file.write(filebody)
    unsigned_file.close()

    signed_file = tempfile.NamedTemporaryFile(delete=False)
    signed_file.close()

    authenticode_sign_binary(hostname, unsigned_file.name, signed_file.name)

    with open(signed_file.name) as f:
        contents = f.read()

    unlink(signed_file.name)
    unlink(unsigned_file.name)

    if len(contents) == 0:
        raise Exception('Could not sign this file.')
    return contents
