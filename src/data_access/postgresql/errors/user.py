
class UserNotFoundError(Exception):
    """Use this class when the database does not contain the User you are looking for"""
    
class ClaimsNotFoundError(Exception):
    """Use this class when the database does not contain any user claims you are looking for"""

