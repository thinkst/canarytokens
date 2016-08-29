"""
A Canarydrop ties a canarytoken to an alerting mechanisms,
and records accounting information about the Canarytoken.

Maps to the object stored in Redis.
"""

import datetime
import random
import md5

from constants import OUTPUT_CHANNEL_EMAIL, OUTPUT_CHANNEL_TWILIO_SMS,\
                      OUTPUT_CHANNEL_WEBHOOK
from queries import get_all_canary_sites, get_all_canary_path_elements,\
     get_all_canary_pages, get_all_canary_domains, get_all_canary_nxdomains,\
     load_user
from tokens import Canarytoken
from users import User, AnonymousUser
from exception import NoUser, NoCanarytokenPresent, UnknownAttribute

class Canarydrop(object):
    allowed_attrs = ['alert_email_enabled', 'alert_email_recipient',\
             'alert_sms_enabled', 'alert_sms_recipient',\
             'alert_webhook_enabled', 'alert_webhook_url','canarytoken',\
             'triggered_count', 'triggered_list','memo', 'generated_url',\
             'generated_email', 'generated_hostname','timestamp', 'user',
             'imgur_token' ,'imgur', 'auth']

    def __init__(self, generate=False, **kwargs):
        self._drop = {}
        for k, v in kwargs.iteritems():
            if k not in self.allowed_attrs:
                raise UnknownAttribute(attribute=k)
            self._drop[k] = v

        if 'canarytoken' not in self._drop:
            raise NoCanarytokenPresent()

        if 'timestamp' not in self._drop:
            self._drop['timestamp'] = datetime.datetime.utcnow()\
                                        .strftime("%s.%f")

        if 'imgur_token' in self._drop and not self._drop['imgur_token']['id']:
            raise Exception('Missing imgur_token from Canarydrop')

        if 'user' not in self._drop or self._drop['user'] in ('None', 'Anonymous'):
            self._drop['user'] = AnonymousUser()
        else:
            self._drop['user'] = load_user(self._drop['user'])
            if not self._drop['user']:
                raise NoUser()

        if 'auth' not in self._drop:
            self._drop['auth'] = md5.md5(str(random.SystemRandom()\
                                  .randrange(1,2**128))).hexdigest()

        if self._drop.get('alert_email_enabled', '') in ('True', True):
            self._drop['alert_email_enabled'] = True
        else:
            self._drop['alert_email_enabled'] = False

        if self._drop.get('alert_webhook_enabled', '') in ('True', True):
            self._drop['alert_webhook_enabled'] = True
        else:
            self._drop['alert_webhook_enabled'] = False

        if self._drop.get('alert_sms_enabled', '') in ('True', True):
            self._drop['alert_sms_enabled'] = True
        else:
            self._drop['alert_sms_enabled'] = False

        if generate:
            self.generate_random_url()
            self.generate_random_hostname()

    def generate_random_url(self,):
        """Return a URL generated at random with the saved Canarytoken.
           The random URL is also saved into the Canarydrop."""
        sites = get_all_canary_sites()
        path_elements = get_all_canary_path_elements()
        pages = get_all_canary_pages()

        generated_url = sites[random.randint(0,len(sites)-1)]+'/'
        path = []
        for count in range(0,random.randint(1,4)):
            if len(path_elements) == 0:
                break

            elem = path_elements[random.randint(0,len(path_elements)-1)]
            path.append(elem)
            path_elements.remove(elem)
        path.append(self._drop['canarytoken'])

        path.append(pages[random.randint(0,len(pages)-1)])

        generated_url += '/'.join(path)

        self._drop['generated_url'] = generated_url

        return self._drop['generated_url']

    def get_random_site(self,):
        sites = get_all_canary_sites()
        return sites[random.randint(0,len(sites)-1)]

    def get_url(self,):
        if 'generated_url' in self._drop:
            return self._drop['generated_url']
        return self.generate_random_url()

    def generate_random_hostname(self, with_random=False, nxdomain=False):
        """Return a hostname generated at random with the saved Canarytoken.
           The random hostname is also saved into the Canarydrop."""
        if nxdomain:
            domains = get_all_canary_nxdomains()
        else:
            domains = get_all_canary_domains()

        if with_random:
            generated_hostname = str(random.randint(1,2**24))+'.'
        else:
            generated_hostname = ''

        generated_hostname += self._drop['canarytoken']+'.'+\
                              domains[random.randint(0,len(domains)-1)]
        return generated_hostname

    def get_hostname(self, with_random=False, as_url=False, nxdomain=False):
        if nxdomain:
            if 'generated_nx_hostname' not in self._drop:
                self._drop['generated_nx_hostname'] = \
                    self.generate_random_hostname(with_random=with_random, nxdomain=True)
            return ('http://' if as_url else '')+self._drop['generated_nx_hostname']
        else:
            if 'generated_hostname' not in self._drop:
                self._drop['generated_hostname'] = \
                    self.generate_random_hostname(with_random=with_random, nxdomain=False)
            return ('http://' if as_url else '')+self._drop['generated_hostname']

    def get_requested_output_channels(self,):
        """Return a list containing the output channels configured in this
           Canarydrop."""
        channels = []
        if (self._drop.get('alert_email_enabled', False) and
                self._drop.get('alert_email_recipient', None)):
            channels.append(OUTPUT_CHANNEL_EMAIL)
        if (self._drop.get('alert_webhook_enabled', False) and
                self._drop.get('alert_webhook_url', None)):
            channels.append(OUTPUT_CHANNEL_WEBHOOK)
        if (self._drop.get('alert_sms_enabled', False) and
                self._drop.get('alert_sms_recipient', None)):
            channels.append(OUTPUT_CHANNEL_TWILIO_SMS)
        return channels

    @property
    def canarytoken(self):
        """Return the Canarydrop's Canarytoken object."""
        return Canarytoken(value=self._drop['canarytoken'])

    @property
    def memo(self):
        """Return the Canarydrop's memo."""
        return self._drop['memo']

    @property
    def user(self):
        return self._drop['user']

    @property
    def imgur_token(self):
        return self._drop['imgur_token']

    @imgur_token.setter
    def imgur_token(self, value):
        self._drop['imgur_token'] = value

    def serialize(self,):
        """Return a representation of this Canarydrop suitable for saving
           into redis."""
        serialized = self._drop.copy()

        if serialized['user']:
            serialized['user'] = serialized['user'].username

        return serialized

    def alertable(self,):
        if self.user.can_send_alert(canarydrop=self):
            return True
        else:
            return False

    def alerting(self,):
        self.user.do_accounting(canarydrop=self)

    def __getitem__(self, key):
        return self._drop[key]

    def __setitem__(self, key, value):
        self._drop[key] = value
