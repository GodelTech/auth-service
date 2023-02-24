class GrantNotFoundError(Exception):
    """Use this class when the database does not contain the Grant you are looking for"""

class PKCEError(Exception):
    """Wrong code challenge"""

class NoScopeError(Exception):
    """PKCE flow needs scope to work"""