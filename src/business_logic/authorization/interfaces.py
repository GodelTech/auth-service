from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.data_access.postgresql.repositories import (
        PersistentGrantRepository,
        UserRepository,
    )


class AuthServiceProtocol(Protocol):
    """
    Protocol defining the interface for an authorization service.

    Implementations of this protocol should provide the `get_redirect_url` method to generate the redirect URL
    for the specified authorization request.

    The `get_redirect_url` method takes an `AuthRequestModel` object as input and returns a string representing
    the redirect URL.

    Implementations may define additional methods as required by the specific authorization service.

    Note: This is a protocol definition and not an actual implementation.
    """

    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        """
        Get the redirect URL for the specified authorization request.

        Args:
            request_data: An instance of AuthRequestModel containing the request data.

        Returns:
            The redirect URL as a string.
        """
        ...


class HasPersistentGrantAndUserRepoProtocol(Protocol):
    """
    Protocol for type hinting mixin methods that require persistent grant and user repositories.

    Implementations of this protocol should provide the `_persistent_grant_repo` and `_user_repo` properties,
    which should return instances of `PersistentGrantRepository` and `UserRepository` respectively.

    Note: This is a protocol definition and not an actual implementation.
    """

    @property
    def _persistent_grant_repo(self) -> PersistentGrantRepository:
        """
        Get the persistent grant repository.

        Returns:
            An instance of `PersistentGrantRepository`.
        """
        ...

    @property
    def _user_repo(self) -> UserRepository:
        """
        Get the user repository.

        Returns:
            An instance of `UserRepository`.
        """
        ...
