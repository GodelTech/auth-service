from business_logic.endsession.dto import RequestEndSessionModel
from src.data_access.postgresql.repositories import PersistentGrantRepository
from typing import Any

class ValidateIdTokenHint:
    """
    Checks that id_token_hint exists.
    """
    def __init__(
            self,
            persistent_grant_repo: PersistentGrantRepository
    ):
        self._persistant_grant_repo = persistent_grant_repo

    async def __call__(self, decoded_id_token_hint: dict[str, Any]):
        pass
        # if await request.id_token_hint == self._persistant_grant_repo
