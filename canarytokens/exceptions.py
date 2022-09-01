class CanaryTokenCreationError(Exception):
    ...


class RecreatingDBException(Exception):
    pass


class NoCanarytokenFound(Exception):
    # TODO: there should be only one exception for a
    # canarytoken not found.
    pass


class NoCanarytokenPresent(Exception):
    # TODO: there should be only one exception for a
    # canarytoken not found.
    pass


class NoUser(Exception):
    pass


class UnknownAttribute(Exception):
    pass


class DuplicateChannel(Exception):
    pass


class InvalidChannel(Exception):
    pass


class CanarydropAuthFailure(Exception):
    ...
