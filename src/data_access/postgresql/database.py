import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from src.config.settings.app import AppSettings

logger = logging.getLogger("is_app")


class Database:
    def __init__(self, database_url: str, max_connection_count: int):
        self.__engine = self._create_connection_pool(
            database_url, max_connection_count
        )
        self.__session_factory = sessionmaker(
            self.__engine, expire_on_commit=False, class_=AsyncSession
        )

    @property
    def session_factory(self):
        return self.__session_factory

    @property
    def engine(self):
        return self.__engine

    def _create_connection_pool(self, db_url: str, max_connection_count: int):
        logger.info("Creating PostgreSQL connection pool.")

        connection_pool = create_async_engine(db_url, poolclass=NullPool)

        logger.info("Connection pool created.")

        return connection_pool

    async def get_connection(self):
        async with self.__session_factory() as session:
            yield session
