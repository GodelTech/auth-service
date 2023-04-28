import logging


from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from dynaconf import Dynaconf


logger = logging.getLogger(__name__)


async def connect_to_db(app: FastAPI, settings: Dynaconf) -> None:
    logger.info('Creating PostgreSQL connection pool.')
    
    app.state.pool = create_async_engine(
        str(settings.DATABASE_URL),
        pool_size=settings.max_connection_count
    )

    logger.info('Connection pool created.')


async def close_db_connection(app: FastAPI) -> None:
    logger.info('Closing connection pool.')

    await app.state.pool.dispose()

    logger.info('Connection pool closed.')