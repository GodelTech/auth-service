from __future__ import annotations

from typing import TYPE_CHECKING

from src.data_access.postgresql.errors import ClientScopesError
from src.business_logic.services.scope import ScopeService
if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import ClientRepository


class ScopeValidator:
    def __init__(self, client_repo: ClientRepository, scope_service: ScopeService):
        self._client_repo = client_repo
        self.scope_service = scope_service
        

    async def __call__(self, scope: str, client_id: str) -> None:
        """
        Validates the scope for a given client.

        Args:
            scope (str): The scope to be validated.
            client_id (str): The ID of the client.

        Raises:
            ClientScopesError: If the scope is invalid.
        """
        scopes_list = await self._client_repo.list_all_scopes_by_client(
            client_id=client_id
        )
        full_names_scope_list = await self.scope_service.get_full_names(scope)
        if not all(scope in scopes_list for scope in full_names_scope_list):
            raise ClientScopesError("Invalid scope.")
