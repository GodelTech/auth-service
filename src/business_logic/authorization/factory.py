from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, TypeVar, Any
from typing_extensions import ParamSpec

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
from .interfaces import AuthServiceProtocol

if TYPE_CHECKING:
    from src.business_logic.services import JWTService, PasswordHash
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        DeviceRepository,
        PersistentGrantRepository,
        UserRepository,
    )


F = TypeVar("F", bound=Callable[..., Any])
FactoryMethod = Callable[..., AuthServiceProtocol]
ResponseTypeToFactoryMethod = Dict[str, FactoryMethod]


def register_factory(response_type: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        AuthServiceFactory._register_factory(response_type, func)
        return func

    return decorator


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


@register_factory(ResponseType.CODE.value)
def _create_code_auth_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    persistent_grant_repo: PersistentGrantRepository,
    password_service: PasswordHash,
    **kwargs: Any,
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


@register_factory(ResponseType.DEVICE.value)
def _create_device_auth_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    persistent_grant_repo: PersistentGrantRepository,
    device_repo: DeviceRepository,
    password_service: PasswordHash,
    **kwargs: Any,
) -> AuthServiceProtocol:
    return DeviceAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(client_repo),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
        user_code_validator=UserCodeValidator(device_repo),
        persistent_grant_repo=persistent_grant_repo,
        device_repo=device_repo,
        user_repo=user_repo,
    )


@register_factory(ResponseType.TOKEN.value)
def _create_token_auth_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    password_service: PasswordHash,
    jwt_service: JWTService,
    **kwargs: Any,
) -> AuthServiceProtocol:
    return TokenAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(client_repo),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
    )


@register_factory(ResponseType.ID_TOKEN.value)
def _create_id_token_auth_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    password_service: PasswordHash,
    jwt_service: JWTService,
    **kwargs: Any,
) -> AuthServiceProtocol:
    return IdTokenAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(client_repo),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
    )


@register_factory(ResponseType.ID_TOKEN_TOKEN.value)
def _create_id_token_token_auth_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    password_service: PasswordHash,
    jwt_service: JWTService,
    **kwargs: Any,
) -> AuthServiceProtocol:
    return IdTokenTokenAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(client_repo),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
    )
