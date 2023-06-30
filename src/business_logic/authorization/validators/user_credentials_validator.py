from __future__ import annotations

from typing import TYPE_CHECKING

from src.data_access.postgresql.errors import (
    UserNotFoundError,
    WrongPasswordError,
)

if TYPE_CHECKING:
    from pydantic import SecretStr

    from src.business_logic.services.password import PasswordHash
    from src.data_access.postgresql.repositories import UserRepository


class UserCredentialsValidator:
    """Validates the requested user credentials against the credentials stored in the database."""

    def __init__(
        self, user_repo: UserRepository, password_service: PasswordHash
    ):
        """
        Initializes a UserCredentialsValidator object.

        Args:
            user_repo (UserRepository): The repository for accessing user information.
            password_service (PasswordHash): The service for hashing and validating passwords.
        """
        self._user_repo = user_repo
        self._password_service = password_service

    async def __call__(self, username: str, password: SecretStr) -> None:
        """
        Validates the user credentials.

        Args:
            username (str): The username to be validated.
            password (SecretStr): The password to be validated.

        Raises:
            UserNotFoundError: If the username or password is invalid.
            WrongPasswordError: If the password is incorrect.
        """
        if not await self._user_repo.exists_user(username):
            raise UserNotFoundError("Invalid username or password.")

        hashed_password = (
            await self._user_repo.get_hashed_password_by_username(username)
        )
        if not self._password_service.is_password_valid(
            password, hashed_password
        ):
            raise WrongPasswordError("Invalid username or password.")
