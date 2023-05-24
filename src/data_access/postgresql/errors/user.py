class UserNotFoundError(Exception):
    """Use this class when the database does not contain the User you are looking for"""

class NoPasswordError(Exception):
    """Use this class when the database does not contain the Password for User"""

class ClaimsNotFoundError(Exception):
    """Use this class when the database does not contain any user claims you are looking for"""


class DuplicationError(Exception):
    """Use this class when the database already contain row with the same cell, that has to be unic"""
    
class NotCompleteScopeError(Exception):
    """Use this class when the database don't contain all required claims for user"""

