from sqlalchemy.ext.asyncio import AsyncEngine
from typing import Generator
from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
    GroupRepository,
    PersistentGrantRepository,
    RoleRepository,
    ThirdPartyOIDCRepository,
    UserRepository,
    WellKnownRepository,
    BlacklistedTokenRepository,
    ResourcesRepository
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


def provide_third_party_oidc_repo(session: AsyncSession) -> ThirdPartyOIDCRepository:
    return ThirdPartyOIDCRepository(session=session)


def provide_client_repo_stub() -> None:  # pragma: no cover
    ...


def provide_client_repo(session: AsyncSession) -> ClientRepository:
    return ClientRepository(session=session)


def provide_user_repo_stub() -> None:  # pragma: no cover
    ...


def provide_user_repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session=session)


def provide_persistent_grant_repo_stub() -> None:  # pragma: no cover
    ...


def provide_persistent_grant_repo(
    session: AsyncSession,
) -> PersistentGrantRepository:
    return PersistentGrantRepository(session=session)


def provide_group_repo(session: AsyncSession) -> GroupRepository:
    return GroupRepository(session=session)


def provide_role_repo(session: AsyncSession) -> RoleRepository:
    return RoleRepository(session=session)


def provide_device_repo_stub() -> None:  # pragma: no cover
    ...


def provide_device_repo(session: AsyncSession) -> DeviceRepository:
    return DeviceRepository(session)


def provide_blacklisted_repo_stub(engine: AsyncEngine) -> None:
    ...


def provide_blacklisted_repo(session: AsyncSession) -> BlacklistedTokenRepository:
    return BlacklistedTokenRepository(session=session)

def provide_async_session(engine: AsyncEngine) -> AsyncSession:
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)()


def provide_async_session_stub() -> None:
    ...

class ProviderSession:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    async def __call__(self) -> Generator[AsyncSession, None, None]:
        async with self._session_factory() as session:
            try:
                yield session
            except:
                await session.close()
