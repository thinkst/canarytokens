class CanaryTokenCreationError(Exception):
    ...


class RecreatingDBException(Exception):
    pass


class NoCanarytokenFound(Exception):
    # TODO: there should be only one exception for a
    # canarytoken not found.
    pass


class NoCanarydropFound(Exception):
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
    pass


class OperationNotAllowed(Exception):
    """
    Exception raised when an operation is not allowed for the current canarytoken.
    For example, trying to perform check-role on a canarytoken that is not in the role-checking state.
    """

    pass
