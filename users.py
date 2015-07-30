"""
Class that encapsulates a user identity. Unused for now.
"""

from exception import UnknownAttribute, MissingAttribute
from queries import lookup_canarytoken_alert_count, save_canarytoken_alert_count
import settings

class User(object):
    allowed_attrs = ['username', 'alert_count']

    def __init__(self, alert_expiry=1, alert_limit=100, **kwargs):
        """Return a new UserPolicy object.

           Arguments:

           alert_expiry -- The delay after a successful alert after which
                           the limit no longer applies.
           alert_limit  -- The number of alerts allowed.
        """

        self.alert_expiry = alert_expiry
        self.alert_limit  = alert_limit

        self._user = {}
        for k, v in kwargs.iteritems():
            if k not in self.allowed_attrs:
                raise UnknownAttribute(attribute=k)
            self._user[k] = v

        if 'username' not in self._user:
            raise MissingAttribute(attribute=username)

    def is_anonymous(self,):
        return self._user['username'] == 'Anonymous'

    def can_send_alert(self, canarydrop=None):
        try:
            alert_count = int(lookup_canarytoken_alert_count(
                                    canarydrop.canarytoken))
        except TypeError:
            return True

        if alert_count + 1 <= self.alert_limit:
            return True

        return False

    def do_accounting(self, canarydrop=None):
        try:
            alert_count = int(lookup_canarytoken_alert_count(
                                    canarydrop.canarytoken))+1
        except TypeError:
            alert_count = 1

        save_canarytoken_alert_count(canarydrop.canarytoken, alert_count,
                                    self.alert_expiry)

    @property
    def username(self,):
        return self._user['username']

class AnonymousUser(User):
    """Represents an anonymous user. These users have lower limits than 
       regular users."""
    def __init__(self):
        User.__init__(self, username='Anonymous', 
                      alert_expiry=(5 if settings.DEBUG else 60), 
                      alert_limit=1)
