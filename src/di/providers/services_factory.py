from typing import TYPE_CHECKING

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
