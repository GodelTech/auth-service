from __future__ import annotations
from typing import Protocol, TYPE_CHECKING


if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.data_access.postgresql.repositories import (
        PersistentGrantRepository,
        UserRepository,
    )


class AuthServiceProtocol(Protocol):
    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        ...


class HasPersistentGrantAndUserRepoProtocol(Protocol):
    """Protocol for type hinting mixin methods, which use persistent grant and user repos."""

    @property
    def _persistent_grant_repo(self) -> PersistentGrantRepository:
        ...

    @property
    def _user_repo(self) -> UserRepository:
        ...
