from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.authorization.constants import ResponseType
from src.data_access.postgresql.errors import WrongResponseTypeError

from ..interfaces import AuthServiceProtocol
from .factory_methods import (
    _create_code_auth_service,
    _create_device_auth_service,
    _create_id_token_auth_service,
    _create_id_token_token_auth_service,
    _create_token_auth_service,
)

from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
    PersistentGrantRepository,
    UserRepository,
)

if TYPE_CHECKING:
    from src.business_logic.services import JWTService, PasswordHash, ScopeService


FactoryMethod = Callable[..., AuthServiceProtocol]
ResponseTypeToFactoryMethod = Dict[str, FactoryMethod]


class AuthServiceFactory:
    """
    Factory class for creating instances of AuthServiceProtocol based on the response type.

    Usage:
    - Register response types and corresponding factory methods before creating instances:
        AuthServiceFactory._register_factory(ResponseType.CODE.value, _create_code_auth_service)

    - Create an instance of AuthServiceFactory in presentation layer:
        factory = AuthServiceFactory(session, client_repo, user_repo, persistent_grant_repo,
                                 device_repo, password_service, jwt_service)

    - Get an authentication service instance based on the response type in presentation layer:
        service = factory.get_service_impl(response_type)
    """

    _response_type_to_factory_method: ResponseTypeToFactoryMethod = {}

    def __init__(
        self,
        session: AsyncSession,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        device_repo: DeviceRepository,
        password_service: PasswordHash,
        jwt_service: JWTService,
        scope_service: ScopeService
    ) -> None:
        """
        Initialize the AuthServiceFactory with the required dependencies.

        Args:
            session: The async SQLAlchemy session.
            client_repo: The repository for accessing client-related data.
            user_repo: The repository for accessing user-related data.
            persistent_grant_repo: The repository for accessing persistent grant-related data.
            device_repo: The repository for accessing device-related data.
            password_service: The service for password hashing and verification.
            jwt_service: The service for JWT generation and verification.
        """
        self.session = session
        self._client_repo = client_repo
        self._user_repo = user_repo
        self._persistent_grant_repo = persistent_grant_repo
        self._device_repo = device_repo
        self._password_service = password_service
        self._jwt_service = jwt_service
        self.scope_service = scope_service

    @classmethod
    def _register_factory(
        cls, response_type: str, factory_method: FactoryMethod
    ) -> None:
        """
        Register a factory method for a specific response type.

        Args:
            response_type: The response type for which the factory method is registered.
            factory_method: The factory method to register.
        """
        cls._response_type_to_factory_method[response_type] = factory_method

    def get_service_impl(self, response_type: str) -> AuthServiceProtocol:
        """
        Get the implementation of AuthServiceProtocol for the specified response type.

        Args:
            response_type: The response type for which to get the service implementation.

        Returns:
            An instance of AuthServiceProtocol for the specified response type.

        Raises:
            WrongResponseTypeError: If the provided response_type is not supported.
        """
        auth_service = self._response_type_to_factory_method.get(response_type)

        if auth_service is None:
            raise WrongResponseTypeError(
                "Provided response_type is not supported."
            )

        return auth_service(  # keyword arguments are required
            client_repo=self._client_repo,
            user_repo=self._user_repo,
            persistent_grant_repo=self._persistent_grant_repo,
            device_repo=self._device_repo,
            password_service=self._password_service,
            jwt_service=self._jwt_service,
            scope_service = self.scope_service
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
