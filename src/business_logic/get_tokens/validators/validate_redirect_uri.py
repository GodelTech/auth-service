from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import ClientRepository


class ValidateRedirectUri:
    def __init__(
            self,
            client_repo: 'ClientRepository'
    ):
        self._client_repo = client_repo
    
    async def __call__(self, redirect_uri: str, client_id: str) -> None:
        uris_list = await self._client_repo.list_all_redirect_uris_by_client(client_id=client_id)
        if redirect_uri not in uris_list:
            raise ValueError("Invalid redirect uri.")
