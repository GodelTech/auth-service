from src.business_logic.get_tokens import TokenServiceFactory
from src.data_access.postgresql.repositories import (
    BlacklistedTokenRepository,
    ClientRepository,
    DeviceRepository,
    PersistentGrantRepository,
    UserRepository,
)
from src.business_logic.jwt_manager.interfaces import JWTServiceProto


def provide_token_service_factory_stub() -> None:
    ...


def provide_token_service_factory(
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
        user_repo: UserRepository,
        device_repo: DeviceRepository,
        jwt_service: JWTServiceProto,
        blacklisted_repo: BlacklistedTokenRepository,
) -> TokenServiceFactory:
    return TokenServiceFactory(
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        user_repo=user_repo,
        device_repo=device_repo,
        jwt_manager=jwt_service,
        blacklisted_repo=blacklisted_repo
    )
