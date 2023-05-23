class IncorrectAuthTokenError(Exception):
    """Use this class when the Authorisation-Token validation fails"""

class NoAuthTokenError(Exception):
    """Use this class when the Authorisation-Token is None"""

class RevokedAuthTokenError(Exception):
    """Use this class when the Authorisation-Token is Revoked"""
