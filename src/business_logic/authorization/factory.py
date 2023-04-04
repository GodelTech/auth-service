from __future__ import annotations
from typing import TYPE_CHECKING
from src.data_access.postgresql.errors import WrongResponseTypeError
from src.business_logic.authorization.service_impls import (
    CodeAuthService,
    DeviceAuthService,
)
from src.business_logic.common.validators import (
    ClientValidator,
    RedirectUriValidator,
)
from src.business_logic.authorization.validators import (
    ScopeValidator,
    UserCredentialsValidator,
)
from src.business_logic.authorization.constants import ResponseType

if TYPE_CHECKING:
    from .interfaces import AuthServiceProtocol
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        UserRepository,
        PersistentGrantRepository,
        DeviceRepository,
    )
    from src.business_logic.services import JWTService, PasswordHash


class AuthServiceFactory:
    def __init__(
        self,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        device_repo: DeviceRepository,
        password_service: PasswordHash,
        jwt_service: JWTService,
    ) -> None:
        self._client_repo = client_repo
        self._user_repo = user_repo
        self._persistent_grant_repo = persistent_grant_repo
        self._device_repo = device_repo
        self._password_service = password_service
        self._jwt_service = jwt_service

    def get_service_impl(self, response_type: str) -> AuthServiceProtocol:
        if response_type == ResponseType.CODE.value:
            return CodeAuthService(
                client_validator=ClientValidator(self._client_repo),
                redirect_uri_validator=RedirectUriValidator(self._client_repo),
                scope_validator=ScopeValidator(self._client_repo),
                user_credentials_validator=UserCredentialsValidator(
                    user_repo=self._user_repo,
                    password_service=self._password_service,
                ),
                persistent_grant_repo=self._persistent_grant_repo,
                user_repo=self._user_repo,
            )
        if response_type == ResponseType.DEVICE.value:
            return DeviceAuthService(
                client_validator=ClientValidator(self._client_repo),
                redirect_uri_validator=RedirectUriValidator(self._client_repo),
                scope_validator=ScopeValidator(self._client_repo),
                user_credentials_validator=UserCredentialsValidator(
                    user_repo=self._user_repo,
                    password_service=self._password_service,
                ),
            )
        raise WrongResponseTypeError(
            "Provided response_type is not supported."
        )
