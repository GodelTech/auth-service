from __future__ import annotations
from typing import TYPE_CHECKING
from src.data_access.postgresql.errors import (
    UserNotFoundError,
    WrongPasswordError,
)

if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import UserRepository
    from src.business_logic.services.password import PasswordHash
    from pydantic import SecretStr


class UserCredentialsValidator:
    def __init__(
        self, user_repo: UserRepository, password_service: PasswordHash
    ):
        self._user_repo = user_repo
        self._password_service = password_service

    async def __call__(self, username: str, password: SecretStr) -> None:
        if not await self._user_repo.exists_user(username):
            raise UserNotFoundError("Invalid username or password.")

        hashed_password = (
            await self._user_repo.get_hashed_password_by_username(username)
        )
        is_password_valid = self._password_service.is_password_valid(
            password, hashed_password
        )
        if not is_password_valid:
            raise WrongPasswordError("Invalid username or password.")
