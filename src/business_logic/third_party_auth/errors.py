class ThirdPartyAuthProviderInvalidRequestDataError(Exception):
    """
    Exception raised when the request data for a third-party authentication provider is invalid.

    This exception is raised when the request data provided for a third-party authentication provider is invalid,
    preventing the authentication process from proceeding.

    """

    ...


class ThirdPartyAuthInvalidStateError(Exception):
    """
    Exception raised when the state in third-party authentication is invalid.

    This exception is raised when the state parameter in a third-party authentication flow is invalid.
    It indicates that the state either already exists or does not match the expected format.

    """

    ...


class UnsupportedThirdPartyAuthProviderError(Exception):
    """
    Exception raised when an unsupported third-party authentication provider is encountered.

    This exception is raised when an unsupported third-party authentication provider is encountered.
    It indicates that the requested provider is not supported by the system.

    """

    ...
