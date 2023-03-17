class ClientBaseException(Exception):
    """Base exception for exceptions related to missing a requested client data in database."""


class ClientNotFoundError(ClientBaseException):
    """Use this class when the database does not contain the client you are looking for."""


class ClientPostLogoutRedirectUriError(ClientBaseException):
    """Use this class when the database does not contain the client post logout uri you are looking for."""


class ClientRedirectUriError(ClientBaseException):
    """Use this class when the database does not contain the client redirect uri you are looking for."""


class ClientGrantsError(ClientBaseException):
    """Use this class when user is in the database but don't have provided grants."""


class ClientScopesError(ClientBaseException):
    """Use this class when the database does not contain the client scopes you are looking for."""
