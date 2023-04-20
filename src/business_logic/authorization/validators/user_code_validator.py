from __future__ import annotations

from typing import TYPE_CHECKING

from src.data_access.postgresql.errors import UserCodeNotFoundError

if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import DeviceRepository


class UserCodeValidator:
    def __init__(self, device_repo: DeviceRepository):
        self._device_repo = device_repo

    async def __call__(self, user_code: str) -> None:
        if not await self._device_repo.exists(user_code):
            raise UserCodeNotFoundError("Incorrect user_code.")


# TODO add validation to check if user_code did expire
