class HTTPXOAuthError(Exception):
    """Base exception class for every httpx-oauth errors."""


class GetIdError(HTTPXOAuthError):
    """Error raised while retrieving user profile from provider API."""
