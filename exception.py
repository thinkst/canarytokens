class UnknownAttribute(Exception):
    def __init__(self, attribute=None):
        self.message = '{attribute} is unrecognized'.format(attribute=attribute)

class MissingAttribute(Exception):
    def __init__(self, attribute=None):
        self.message = '{attribute} is missing'.format(attribute=attribute)

class NoCanarytokenPresent(Exception):
    def __init__(self, attribute=None):
        self.message = '{attribute} is unrecognized'.format(attribute=attribute)

class NoCanarytokenFound(Exception):
    def __init__(self, haystack):
        self._haystack = haystack

    def __str__(self,):
        return 'No Canarytoken found in %s' % self._haystack

class DuplicateChannel(Exception):
    pass

class InvalidChannel(Exception):
    pass

class NoUser(Exception):
    pass

class LinkedInFailure(Exception):
    pass

class BitcoinFailure(Exception):
    pass

class IncompleteRequest(Exception):
    pass

class DuplicateDNSRequest(Exception):
    pass
