import logging
from typing import Optional

from src.business_logic.services.authorization.response_type_handlers.factory import (
    ResponseTypeHandlerFactory,
)
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.password import PasswordHash
from src.data_access.postgresql.errors import ClientScopesError
from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
    PersistentGrantRepository,
    UserRepository,
)
from src.presentation.api.models import DataRequestModel

logger = logging.getLogger(__name__)


class AuthorizationService:
    def __init__(
        self,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        device_repo: DeviceRepository,
        password_service: PasswordHash,
        jwt_service: JWTService,
    ) -> None:
        self._request_model: Optional[DataRequestModel] = None
        self.client_repo = client_repo
        self.user_repo = user_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.device_repo = device_repo
        self.password_service = password_service
        self.jwt_service = jwt_service

    @property
    def request_model(self) -> DataRequestModel:
        if self._request_model is None:
            raise ValueError("Invalid request")
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: DataRequestModel) -> None:
        self._request_model = request_model

    async def _validate_scope(self) -> None:
        # TODO this method also needs to be fixed in client repo I need to make many calls to db to complete an easy task right know
        client_from_db = await self.client_repo.get_client_by_client_id(
            client_id=self.request_model.client_id
        )
        client_scopes = await self.client_repo.get_client_scopes(
            client_id=client_from_db.id  # TODO it should be possible to pass self.request.client_id here directly
        )
        if (
            "user_code" not in self.request_model.scope
            and self.request_model.scope != client_scopes
        ):
            raise ClientScopesError

    async def _validate_auth_data(self) -> int:
        """
        Validates the client_id and client_redirect_uri, retrieves the hashed_password for the given username,
        and validates the provided password. If validation is successful, returns the user_id associated with the
        provided username.

        Raises:
            ClientRedirectUriError: If provided client_redirect_uri is invalid.
            ClientNotFoundError: If provided client_id is invalid.
            UserNotFoundError: If provided username is invalid.
            WrongPasswordError: If the provided password is invalid.

        Returns:
            int: The user_id associated with the provided username.
        """
        # TODO this method actually validates both client_id and redirect_uri -> we need to refactor client repo for sure
        await self.client_repo.validate_client_redirect_uri(
            self.request_model.client_id, self.request_model.redirect_uri
        )
        await self._validate_scope()
        hashed_password, user_id = await self.user_repo.get_hash_password(
            self.request_model.username
        )
        self.password_service.validate_password(
            self.request_model.password, hashed_password
        )
        return user_id

    async def get_redirect_url(self) -> str:
        user_id = await self._validate_auth_data()
        handler = ResponseTypeHandlerFactory.get_handler(
            self.request_model.response_type, auth_service=self
        )
        return await handler.get_redirect_url(user_id)
