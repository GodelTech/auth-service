from __future__ import annotations

from typing import TYPE_CHECKING

from src.data_access.postgresql.errors import ClientScopesError

if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import ClientRepository


class ScopeValidator:
    """Validates the requested scope against the scope stored in the database."""

    def __init__(self, client_repo: ClientRepository):
        """
        Initializes a ScopeValidator object.

        Args:
            client_repo (ClientRepository): The repository for accessing client information.
        """
        self._client_repo = client_repo

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
        if not all(scope in scopes_list[0] for scope in scope.split()):
            raise ClientScopesError("Invalid scope.")
