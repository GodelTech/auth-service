from business_logic.endsession.dto import RequestEndSessionModel
from business_logic.services import JWTService
from src.data_access.postgresql.repositories import PersistentGrantRepository
from typing import Any

class ValidateIdTokenHint:
    """
    Checks that id_token_hint exists.
    """
    def __init__(
            self,
            jwt_service: JWTService
    ):
        self._jwt_service = jwt_service

    async def __call__(self, request_model: RequestEndSessionModel):
        if not await self._jwt_service.verify_token(token=request_model.id_token_hint, aud="admin"):
            raise ###


class ValidateDecodedIdTokenHint:
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
