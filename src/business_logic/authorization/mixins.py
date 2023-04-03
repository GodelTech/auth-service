from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from .interfaces import HasPersistentGrantAndUserRepoProtocol


class CreateGrantMixin:
    async def _create_grant(
        self: HasPersistentGrantAndUserRepoProtocol,
        code: str,
        request_data: AuthRequestModel,
    ) -> None:
        user_id = await self._user_repo.get_user_id_by_username(
            request_data.username
        )
        await self._persistent_grant_repo.create(
            client_id=request_data.client_id, grant_data=code, user_id=user_id
        )


class UpdateRedirectUrlMixin:
    async def _update_redirect_url(
        self: HasPersistentGrantAndUserRepoProtocol,
        request_data: AuthRequestModel,
        redirect_url: str,
    ) -> str:
        if request_data.state:
            redirect_url += f"&state={request_data.state}"
        return redirect_url
