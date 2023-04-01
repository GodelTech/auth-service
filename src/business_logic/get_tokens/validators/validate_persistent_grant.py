from src.business_logic.get_tokens.errors import InvalidGrantError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import PersistentGrantRepository


class ValidatePersistentGrant:
    def __init__(
            self,
            persistent_grant_repo: 'PersistentGrantRepository' 
    ):
        self._persistent_grant_repo = persistent_grant_repo
    

    async def __call__(self, code_to_validate: str, grant_type: str) -> None:
        if not await self._persistent_grant_repo.exists(code_to_validate, grant_type):
            raise InvalidGrantError('Invalid grant value or grant type.')
