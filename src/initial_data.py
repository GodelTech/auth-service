from src.dyna_config import (
    DB_MAX_CONNECTION_COUNT,
    DB_URL,
)
from src.scripts.populate_data.populate_third_party_providers_data import (
    populate_identity_providers,
)
import src.di.providers as prov
import logging
import asyncio

logger = logging.getLogger(__name__)


async def init() -> None:
    db_engine = prov.provide_db(
        database_url=DB_URL, max_connection_count=DB_MAX_CONNECTION_COUNT
    )
    session = prov.provide_async_session(db_engine)
    await populate_identity_providers(session=session)


async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
