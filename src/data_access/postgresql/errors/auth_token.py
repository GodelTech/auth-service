from fastapi import status
class IncorrectAuthTokenError(Exception):
    """Use this class when the Authorisation-Token validation fails."""
    message = {"message": "Incorrect Token"}
    status_code = status.HTTP_401_UNAUTHORIZED