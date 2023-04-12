from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict

from src.data_access.postgresql.errors import WrongResponseTypeError
from ..interfaces import AuthServiceProtocol

from src.business_logic.authorization.constants import ResponseType
from .factory_methods import (
    _create_id_token_token_auth_service,
    _create_code_auth_service,
    _create_device_auth_service,
    _create_id_token_auth_service,
    _create_token_auth_service,
)

if TYPE_CHECKING:
    from src.business_logic.services import JWTService, PasswordHash
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        DeviceRepository,
        PersistentGrantRepository,
        UserRepository,
    )


FactoryMethod = Callable[..., AuthServiceProtocol]
ResponseTypeToFactoryMethod = Dict[str, FactoryMethod]


class AuthServiceFactory:
    _response_type_to_factory_method: ResponseTypeToFactoryMethod = {}

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
        cls, response_type: str, factory_method: FactoryMethod
    ) -> None:
        cls._response_type_to_factory_method[response_type] = factory_method

    def get_service_impl(self, response_type: str) -> AuthServiceProtocol:
        auth_service = self._response_type_to_factory_method.get(response_type)

        if auth_service is None:
            raise WrongResponseTypeError(
                "Provided response_type is not supported."
            )

        return auth_service(
            client_repo=self._client_repo,
            user_repo=self._user_repo,
            persistent_grant_repo=self._persistent_grant_repo,
            device_repo=self._device_repo,
            password_service=self._password_service,
            jwt_service=self._jwt_service,
        )


AuthServiceFactory._register_factory(
    ResponseType.CODE.value, _create_code_auth_service
)
AuthServiceFactory._register_factory(
    ResponseType.DEVICE.value, _create_device_auth_service
)
AuthServiceFactory._register_factory(
    ResponseType.TOKEN.value, _create_token_auth_service
)
AuthServiceFactory._register_factory(
    ResponseType.ID_TOKEN.value, _create_id_token_auth_service
)
AuthServiceFactory._register_factory(
    ResponseType.ID_TOKEN_TOKEN.value, _create_id_token_token_auth_service
)
