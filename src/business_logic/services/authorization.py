import logging
import secrets

from src.business_logic.services.password import PasswordHash
from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository,
)
from src.presentation.api.models import RequestModel


logger = logging.getLogger('is_app')


class AuthorizationService:
    def __init__(
        self,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        password_service: PasswordHash
    ) -> None:
        self._request_model = None
        self.client_repo = client_repo
        self.user_repo = user_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.password_service = password_service

    async def get_redirect_url(self) -> str:

        if await self._validate_client(self.request_model.client_id):
            scope_data = await self._parse_scope_data(
                scope=self.request_model.scope
            )
            password = scope_data["password"]
            user_name = scope_data["username"]

            (
                user_hash_password,
                user_id,
            ) = await self.user_repo.get_hash_password(user_name)
            validated = self.password_service.validate_password(
                password, user_hash_password
            )

            if user_hash_password and validated:
                secret_code = secrets.token_urlsafe(32)
                await self.persistent_grant_repo.create(
                    client_id=self.request_model.client_id,
                    data=secret_code,
                    user_id=user_id,
                )

                return await self._update_redirect_url_with_params(
                    secret_code=secret_code
                )

    async def _validate_client(self, client_id: str) -> bool:
        """
        Checks if the client is in the database.
        """
        client = await self.client_repo.get_client_by_client_id(
            client_id=client_id
        )
        return client

    async def _parse_scope_data(self, scope: str) -> dict:
        """ """
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in scope.split("&")[1:]
        }

    async def _update_redirect_url_with_params(self, secret_code: str) -> str:
        redirect_uri = f"{self.request_model.redirect_uri}?code={secret_code}"
        if self.request_model.state:
            redirect_uri += f"&state={self.request_model.state}"

        return redirect_uri

    @property
    def request_model(self) -> None:
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: RequestModel) -> None:
        self._request_model = request_model
