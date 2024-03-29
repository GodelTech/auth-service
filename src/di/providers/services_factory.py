from sqlalchemy.ext.asyncio import AsyncSession
from src.business_logic.authorization import AuthServiceFactory
from src.data_access.postgresql.repositories import (
    ClientRepository,
    UserRepository,
    PersistentGrantRepository,
    DeviceRepository,
    ThirdPartyOIDCRepository,
)
from httpx import AsyncClient
from src.business_logic.third_party_auth.factory import (
    ThirdPartyAuthServiceFactory,
)

from src.business_logic.services import JWTService, PasswordHash


def provide_auth_service_factory(
    session: AsyncSession,
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
    user_repo: UserRepository,
    device_repo: DeviceRepository,
    jwt_service: JWTService,
    password_service: PasswordHash,
) -> AuthServiceFactory:
    return AuthServiceFactory(
        session=session,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        user_repo=user_repo,
        device_repo=device_repo,
        jwt_service=jwt_service,
        password_service=password_service,
    )


def provide_third_party_auth_service_factory(
    session: AsyncSession,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    async_http_client: AsyncClient,
) -> ThirdPartyAuthServiceFactory:
    return ThirdPartyAuthServiceFactory(
        session=session,
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        async_http_client=async_http_client,
    )
