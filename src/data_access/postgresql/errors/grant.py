class GrantBaseException(Exception):
    """Base exception for exceptions related to missing a requested grant data in database."""


class GrantNotFoundError(GrantBaseException):
    """Use this class when the database does not contain the Grant you are looking for"""


class GrantTypeNotSupported(GrantBaseException):
    """Use this class when provided grant_type is not suported - does not exist in a database."""
