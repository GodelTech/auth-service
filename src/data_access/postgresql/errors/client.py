class ClientNotFoundError(Exception):
    """Use this class when the database does not contain the client you are looking for"""


class ClientPostLogoutRedirectUriError(Exception):
    """Use this class when the database does not contain the client post logout uri you are looking for"""


class WrongGrantsError(Exception):
    """Use this class when user is in the database but don't have"""
