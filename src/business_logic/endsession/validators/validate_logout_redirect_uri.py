from src.data_access.postgresql.repositories.client import ClientRepository
from src.business_logic.endsession.dto import RequestEndSessionModel
from src.data_access.postgresql.repositories import PersistentGrantRepository
from src.business_logic.endsession.errors import InvalidLogoutRedirectUriError
from typing import Any

class ValidateLogoutRedirectUri:
    """
    Checks that id_token_hint exists.
    """
    def __init__(
            self,
            client_repo: ClientRepository
    ):
        self._client_repo = client_repo

    async def __call__(self, request_model: RequestEndSessionModel,
                       client_id: str) -> None:
        if not await self._client_repo.validate_post_logout_redirect_uri(
                                            client_id,
                                            request_model.post_logout_redirect_uri,
                                            ):
            raise InvalidLogoutRedirectUriError("Invalid post logout redirect uri")
