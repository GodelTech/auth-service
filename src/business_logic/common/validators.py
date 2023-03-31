from typing import TYPE_CHECKING
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientRedirectUriError,
)

if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import ClientRepository


class ClientValidator:
    def __init__(self, client_repo: ClientRepository) -> None:
        self._client_repo = client_repo

    async def __call__(self, client_id: str) -> None:
        if not await self._client_repo.exists(client_id=client_id):
            raise ClientNotFoundError("Incorrect client_id.")


class RedirectUriValidator:
    def __init__(self, client_repo: ClientRepository) -> None:
        self._client_repo = client_repo

    async def __call__(self, redirect_uri: str, client_id: str) -> None:
        uris_list = await self._client_repo.list_all_redirect_uris_by_client(
            client_id=client_id
        )
        if redirect_uri not in uris_list:
            raise ClientRedirectUriError("Invalid redirect_uri.")
