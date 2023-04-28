from sqlalchemy.ext.asyncio import AsyncEngine

from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
    GroupRepository,
    PersistentGrantRepository,
    RoleRepository,
    ThirdPartyOIDCRepository,
    UserRepository,
    WellKnownRepository,
    BlacklistedTokenRepository
)
from src.data_access.postgresql.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


def provide_wellknown_repo_stub() -> None:  # pragma: no cover
    ...


def provide_wellknown_repo(
    engine: AsyncEngine,
) -> WellKnownRepository:
    return WellKnownRepository(engine)

def provide_third_party_oidc_repo_stub() -> None:  # pragma: no cover
    ...


def provide_third_party_oidc_repo(
    engine: AsyncEngine,
) -> ThirdPartyOIDCRepository:
    return ThirdPartyOIDCRepository(engine)


def provide_client_repo_stub() -> None:  # pragma: no cover
    ...


def provide_client_repo(engine: AsyncEngine) -> ClientRepository:
    return ClientRepository(engine)


def provide_user_repo_stub() -> None:  # pragma: no cover
    ...


def provide_user_repo() -> UserRepository:
    return UserRepository()


def provide_persistent_grant_repo_stub() -> None:  # pragma: no cover
    ...


def provide_persistent_grant_repo(
    engine: AsyncEngine,
) -> PersistentGrantRepository:
    return PersistentGrantRepository(engine)


def provide_group_repo(engine: AsyncEngine) -> GroupRepository:
    return GroupRepository(engine)


def provide_role_repo() -> RoleRepository:
    return RoleRepository()


def provide_device_repo_stub() -> None:  # pragma: no cover
    ...


def provide_device_repo(engine: AsyncEngine) -> DeviceRepository:
    return DeviceRepository(engine)


def provide_blacklisted_repo_stub(engine: AsyncEngine) -> None:
    ...


def provide_blacklisted_repo(engine: AsyncEngine) -> BlacklistedTokenRepository:
    return BlacklistedTokenRepository(engine)

def provide_async_session(engine: AsyncEngine) -> AsyncSession:
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)()