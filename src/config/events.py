from typing import Callable

from fastapi import FastAPI

from src.config.settings.app import AppSettings
from src.data_access.postgresql.events import connect_to_db, close_db_connection


def create_start_app_handler(
    app: FastAPI,
    settings: AppSettings,
) -> Callable:
    async def start_app() -> None:
        await connect_to_db(app, settings)

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await close_db_connection(app)

    return stop_app
