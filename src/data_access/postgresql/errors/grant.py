class GrantNotFoundError(Exception):
    """Use this class when the database does not contain the Grant you are looking for"""


class GrantTypeNotSupported(Exception):
    """Use this class when provided grant_type is not suported - does not exist in a database."""
