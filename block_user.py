import argparse
from queries import block_domain, block_email, is_email_blocked

parser = argparse.ArgumentParser(description='Block emails or domains from creating canarytokens')
parser.add_argument('users', metavar='user', type=str, nargs='+',
                    help='an email address or domain to block')
args = parser.parse_args()

for user in args.users:
    if '@' in user:
        kind, block_func, test_target = 'email',  block_email,  user
    else:
        kind, block_func, test_target = 'domain', block_domain, 'anything@'+user
    try:
        print('\n[*] blocking {}: "{}"'.format(kind, user))
        block_func(user)
        print('[>]     checking "{}" is blocked'.format(test_target))
        assert is_email_blocked(test_target)
        print('[o]     successfully blocked "{}"'.format(test_target))
    except:
        print('[x]     failed to block "{}"'.format(test_target))

print('\n[;] done blocking')