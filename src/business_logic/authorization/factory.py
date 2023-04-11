from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from src.business_logic.authorization.constants import ResponseType
from src.business_logic.authorization.service_impls import (
    CodeAuthService,
    DeviceAuthService,
    TokenAuthService,
    IdTokenAuthService,
    IdTokenTokenAuthService,
)
from src.business_logic.authorization.validators import (
    ScopeValidator,
    UserCredentialsValidator,
    UserCodeValidator,
)
from src.business_logic.common.validators import (
    ClientValidator,
    RedirectUriValidator,
)
from src.data_access.postgresql.errors import WrongResponseTypeError

if TYPE_CHECKING:
    from src.business_logic.services import JWTService, PasswordHash
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        DeviceRepository,
        PersistentGrantRepository,
        UserRepository,
    )

    from .interfaces import AuthServiceProtocol


class AuthServiceFactory:
    _response_type_service_mapper = {}

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

    @classmethod
    def _register_factory(
        cls, response_type: str, factory_method: Callable
    ) -> None:
        cls._response_type_service_mapper[response_type] = factory_method

    def get_service_impl(self, response_type: str) -> AuthServiceProtocol:
        factory = self._response_type_service_mapper.get(response_type)

        if factory is None:
            raise WrongResponseTypeError(
                "Provided response_type is not supported."
            )

        return factory(
            client_repo=self._client_repo,
            user_repo=self._user_repo,
            persistent_grant_repo=self._persistent_grant_repo,
            device_repo=self._device_repo,
            password_service=self._password_service,
            jwt_service=self._jwt_service,
        )


def _create_code_auth_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    persistent_grant_repo: PersistentGrantRepository,
    device_repo: DeviceRepository,
    password_service: PasswordHash,
    jwt_service: JWTService,
) -> AuthServiceProtocol:
    return CodeAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(client_repo),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
        persistent_grant_repo=persistent_grant_repo,
        user_repo=user_repo,
    )


AuthServiceFactory._register_factory(
    ResponseType.CODE.value, _create_code_auth_service
)
