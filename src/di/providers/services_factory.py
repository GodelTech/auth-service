from src.business_logic.authorization import AuthServiceFactory
from src.data_access.postgresql.repositories import (
    ClientRepository,
    UserRepository,
    PersistentGrantRepository,
    DeviceRepository,
)
from src.business_logic.services import JWTService, PasswordHash


def provide_auth_service_factory_stub() -> None:
    ...


def provide_auth_service_factory(
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
    user_repo: UserRepository,
    device_repo: DeviceRepository,
    jwt_service: JWTService,
    password_service: PasswordHash,
) -> AuthServiceFactory:
    return AuthServiceFactory(
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        user_repo=user_repo,
        device_repo=device_repo,
        jwt_service=jwt_service,
        password_service=password_service,
    )
