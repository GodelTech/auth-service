import logging

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio.engine import AsyncEngine

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, database_url: str, max_connection_count: int):
        self.__engine = self._create_connection_pool(
            database_url, max_connection_count
        )
        self.__session_factory = sessionmaker(
            self.__engine, expire_on_commit=False, class_=AsyncSession
        )

    @property
    def session_factory(self) -> AsyncSession:
        return self.__session_factory

    @property
    def engine(self) -> AsyncSession:
        return self.__engine

    @property
    def sync_engine(self) -> Engine:
        return self.__sync_engine

    def _create_connection_pool(self, db_url: str, max_connection_count: int) -> AsyncEngine:
        logger.info("Creating PostgreSQL connection pool.")

        connection_pool = create_async_engine(db_url, poolclass=NullPool)

        logger.info("Connection pool created.")

        return connection_pool

    async def get_connection(self) -> AsyncSession:
        async with self.__session_factory() as session:
            yield session
from sqlalchemy import text
from time import sleep
class DatabaseSync:
    def __init__(self, database_url: str):
        # retry_count = 0
        # while retry_count<6:
        #     try:
                self.__sync_engine = self._create_sync_connection_pool(database_url)
                self.__sync_session_factory = sessionmaker(
                    self.__sync_engine
                )
            #     with self.__sync_session_factory() as sess:
            #         print(sess)
            #         a = sess.execute(text("SELECT * FROM clients"))
            #         print(a)
            #     break
            # except Exception as err:
            #     retry_count+=1
            #     if retry_count<2:
            #         print(err)
            #     sleep(2)

       
    @property
    def sync_engine(self) -> Engine:
        return self.__sync_engine

    @property
    def sync_session_factory(self) -> sessionmaker:
        return self.__sync_session_factory

    def _create_sync_connection_pool(self, db_url:str) -> Engine:
        logger.info("Creating PostgreSQL sync engine.")
        db_url = db_url.replace("asyncpg", "psycopg2")
        sync_engine = create_engine(db_url)

        logger.info("Sync engine created.")

        return sync_engine