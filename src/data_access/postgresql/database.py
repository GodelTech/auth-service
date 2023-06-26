import logging

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from src.config.settings.app import AppSettings

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, database_url: str, max_connection_count: int):
        self.__engine = self._create_connection_pool(
            database_url, max_connection_count
        )
        self.__session_factory = sessionmaker(
            self.__engine, expire_on_commit=False, class_=AsyncSession
        )
        self.__sync_engine = self._create_sync_connection_pool(database_url)
        # self.__sync_session_factory = sessionmaker(
        #     self.__sync_engine, expire_on_commit=False, class_= Session
        # )


    @property
    def session_factory(self) -> AsyncSession:
        return self.__session_factory

    @property
    def engine(self) -> AsyncSession:
        return self.__engine

    @property
    def sync_engine(self) -> Engine:
        return self.__sync_engine

    # @property
    # def sync_session_factory(self) -> Session:
    #     return self.__sync_session_factory

    def _create_connection_pool(self, db_url: str, max_connection_count: int) -> AsyncEngine:
        logger.info("Creating PostgreSQL connection pool.")

        connection_pool = create_async_engine(db_url, poolclass=NullPool)

        logger.info("Connection pool created.")

        return connection_pool

    def _create_sync_connection_pool(self, db_url:str) -> Engine:
        logger.info("Creating PostgreSQL sync engine.")
        # print(db_url)
        db_url = db_url.replace("asyncpg", "psycopg2")
        # print(db_url)
        sync_engine = create_engine(db_url)

        logger.info("Sync engine created.")

        return sync_engine

    async def get_connection(self) -> AsyncSession:
        async with self.__session_factory() as session:
            yield session