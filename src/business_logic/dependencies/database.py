from typing import AsyncGenerator, Callable, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from asyncpg.pool import Pool
from fastapi import Depends

from src.data_access.postgresql.repositories.base import BaseRepository
from src import main


def _get_db_pool() -> Pool:
    return main.app.state.pool


async def _get_connection_from_pool(
    pool: Pool = Depends(_get_db_pool),
) -> AsyncGenerator[Session, None]:
    async_session = sessionmaker(pool, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


def get_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[Session], BaseRepository]:
    def _get_repo(
        session: Session = Depends(_get_connection_from_pool),
    ) -> BaseRepository:
        return repo_type(session)

    return _get_repo
