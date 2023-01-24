from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.repositories import (
    ClientRepository,
    UserRepository,
    PersistentGrantRepository
)

from sqlalchemy.ext.asyncio import AsyncEngine


def provide_client_repo_stub():
    ...


def provide_client_repo(engine: AsyncEngine) -> ClientRepository:
    return ClientRepository(engine)


def provide_user_repo_stub():
    ...


def provide_user_repo(engine: AsyncEngine) -> UserRepository:
    return UserRepository(engine)


def provide_persistent_grant_repo_stub():
    ...


def provide_persistent_grant_repo(engine: AsyncEngine) -> PersistentGrantRepository:
    return PersistentGrantRepository(engine)
