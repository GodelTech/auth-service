from __future__ import annotations

from typing import TYPE_CHECKING

from src.data_access.postgresql.errors import ClientScopesError

if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import ClientRepository


class ScopeValidator:
    def __init__(self, client_repo: ClientRepository):
        self._client_repo = client_repo

    async def __call__(self, scope: str, client_id: str) -> None:
        scopes_list = await self._client_repo.list_all_scopes_by_client(
            client_id=client_id
        )
        if not all(scope in scopes_list for scope in scope.split()):
            raise ClientScopesError("Invalid scope.")
