class TokenBaseException(Exception):
    """Base exception for exceptions related to missing a requested grant data in database."""


class TokenIncorrectError(TokenBaseException):
    """Use this class when the database does not contain the Grant you are looking for"""