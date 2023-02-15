from sqlalchemy.ext.asyncio import AsyncEngine

from src.data_access.postgresql import Database


def provide_db_stub() -> None:
    ...


def provide_db(database_url: str, max_connection_count: int) -> AsyncEngine:
    return Database(
        database_url=database_url, max_connection_count=max_connection_count
    ).engine
