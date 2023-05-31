from __future__ import annotations
from src.business_logic.get_tokens.errors import InvalidClientCredentialsError
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import ClientRepository


class ValidateClientCredentials:
    def __init__(self, client_repo: ClientRepository) -> None:
        self._client_repo = client_repo
    
    async def __call__(self, client_id: str, client_secret: str) -> None:
        if not await self._client_repo.exists_client_with_provided_client_secret(
            client_id=client_id, client_secret=client_secret
        ):
            raise InvalidClientCredentialsError
