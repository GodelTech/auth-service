from src.business_logic.get_tokens.errors import InvalidGrantError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import PersistentGrantRepository


class ValidateGrantByClient:
    """
    Checks that authorization code was issued to the authenticated Client.
    """
    def __init__(
            self,
            persistent_grant_repo: 'PersistentGrantRepository'
    ):
        self._persistent_grant_repo = persistent_grant_repo
    
    async def __call__(self, grant_data: str, client_id: str, grant_type: str) -> None:
        if not await self._persistent_grant_repo.exists_grant_for_client(grant_data, client_id, grant_type):
            raise InvalidGrantError('Invalid data provided.')
