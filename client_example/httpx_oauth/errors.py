class HTTPXOAuthError(Exception):
    """Base exception class for every httpx-oauth errors."""


class GetIdEmailError(HTTPXOAuthError):
    """Error raised while retrieving user profile from provider API."""
