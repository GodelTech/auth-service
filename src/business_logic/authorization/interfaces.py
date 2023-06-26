from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.data_access.postgresql.repositories import (
        PersistentGrantRepository,
        UserRepository,
    )


class AuthServiceProtocol(Protocol):
    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        ...


class HasUserRepoProtocol(Protocol):
    """Protocol for type hinting mixin methods, user repos."""

    @property
    def _user_repo(self) -> UserRepository:
        ...
