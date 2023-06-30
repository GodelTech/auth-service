from __future__ import annotations

import time
from typing import TYPE_CHECKING

from src.data_access.postgresql.errors import (
    UserCodeExpirationTimeError,
    UserCodeNotFoundError,
)

if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import DeviceRepository


class UserCodeValidator:
    """Validates the requested user_code against the user_code stored in the database."""

    def __init__(self, device_repo: DeviceRepository):
        """
        Initializes a UserCodeValidator object.

        Args:
            device_repo (DeviceRepository): The repository for accessing device information.
        """
        self._device_repo = device_repo

    async def __call__(self, user_code: str) -> None:
        """
        Validates a user code.

        Args:
            user_code (str): The user code to be validated.

        Raises:
            UserCodeNotFoundError: If the user code is incorrect.
            UserCodeExpirationTimeError: If the user code has expired.
        """
        if not await self._device_repo.exists(user_code):
            raise UserCodeNotFoundError("Incorrect user_code.")

        if int(
            time.time()
        ) > await self._device_repo.get_expiration_time_by_user_code(
            user_code
        ):
            raise UserCodeExpirationTimeError(
                "Provided user_code has expired."
            )
