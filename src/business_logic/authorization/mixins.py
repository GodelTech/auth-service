from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel


class CreateGrantMixin:
    async def create_grant(self, code: str, request_data: AuthRequestModel):
        user_id = await self._user_repo.get_user_id_by_username(
            request_data.username
        )
        await self._persistent_grant_repo.create(
            client_id=request_data.client_id, grant_data=code, user_id=user_id
        )
