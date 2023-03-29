from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import ClientRepository


class ValidateClient:
    def __init__(
            self,
            client_repo: 'ClientRepository'
    ) -> None:
        self._client_repo = client_repo
    
    async def __call__(self, client_id: str) -> None:
        if not await self._client_repo.exists(client_id=client_id):
            raise ValueError('Incorrect client_id.')
