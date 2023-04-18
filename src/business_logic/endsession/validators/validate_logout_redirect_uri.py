from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories import PersistentGrantRepository
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

    async def __call__(self, request_model, client_id):
        if request_model.post_logout_redirect_uri:
            await self._client_repo.validate_post_logout_redirect_uri(client_id, logout_redirect_uri)
