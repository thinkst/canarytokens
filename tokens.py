import re
import random
from exception import NoCanarytokenFound

canarytoken_ALPHABET=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                    'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3',
                    '4', '5', '6', '7', '8', '9']
canarytoken_LENGTH=25 # equivalent to 128-bit id

class Canarytoken(object):
    CANARY_RE = re.compile('.*(['+''.join(canarytoken_ALPHABET)+']{'+
                          str(canarytoken_LENGTH)+'}).*', re.IGNORECASE)
    def __init__(self, value=None):
        """Create a new Canarytoken instance. If no value was provided, 
           generate a new canarytoken.

           Arguments:
           value -- A user-provided canarytoken. It's format will be validated.

           Exceptions:
           NoCanarytokenFound - Thrown if the supplied canarytoken is not in the
                              correct format.
        """

        if value:
            self._value = self.find_canarytoken(value).lower()
        else:
            self._value = Canarytoken.generate()

    @staticmethod
    def generate():
        """Return a new canarytoken."""
        return ''.join([ canarytoken_ALPHABET[
                    random.randint(0,len(canarytoken_ALPHABET)-1)
                 ]  for x in range(0, canarytoken_LENGTH)])

    @staticmethod
    def find_canarytoken(haystack):
        """Return the canarytoken found in haystack.

           Arguments:
           haystack -- A string that might include a canarytoken.

           Exceptions:
           NoCanarytokenFound
           """
        m = Canarytoken.CANARY_RE.match(haystack)
        if not m:
            raise NoCanarytokenFound(haystack)

        return m.group(1)

    def value(self,):
        return self._value

    def __repr__(self,):
        return '<Canarytoken - %s>' % self._value

if __name__ == '__main__':
    print Canarytoken()
    token = Canarytoken().value()
    print token
    print Canarytoken(value=token)
    
    bad_tokens = []
    #short value
    bad_tokens.append(token[:1])

    #invalid char token
    bad_tokens.append('!'+token[1:])

    for t in bad_tokens:
        try:
            print Canarytoken(value=t)
            assert False
        except NoCanarytokenFound:
            print 'Invalid token %s detected' % t
