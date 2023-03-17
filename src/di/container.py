from dependency_injector import containers, providers

from src.config import get_app_settings
from src.data_access.postgresql import Database


class Container(containers.DeclarativeContainer):
    config = providers.Object(get_app_settings())

    db = providers.Singleton(
        Database,
        database_url=str(config().database_url),
        max_connection_count=config().max_connection_count,
    )
