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


class AWSInfraOperationNotAllowed(Exception):
    """
    Exception raised when an operation is not allowed for the current canarytoken.
    """

    pass


class AWSInfraDataGenerationLimitReached(Exception):
    """
    Exception raised when the data generation limit for a canarytoken is reached.
    """

    pass


class CanarytokenTypeNotEnabled(Exception):
    """
    Exception raised when a canarytoken type is not enabled.
    """

    pass
