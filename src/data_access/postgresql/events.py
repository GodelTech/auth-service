import logging
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from src.config.settings.app import AppSettings


logger = logging.getLogger('is_app')


async def connect_to_db(app: FastAPI, settings: AppSettings) -> None:
    logger.info('Creating PostgreSQL connection pool.')
    
    app.state.pool = create_async_engine(
        str(settings.database_url),
        pool_size=settings.max_connection_count
    )

    logger.info('Connection pool created.')


async def close_db_connection(app: FastAPI) -> None:
    logger.info('Closing PostgreSQL connection pool.')

    await app.state.pool.dispose()

    logger.info('Connection pool closed.')