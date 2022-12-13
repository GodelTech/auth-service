import logging

from src.config.settings.app import AppSettings


class TestAppSettings(AppSettings):
    debug: bool = True

    title: str = "Test IS POC application"

    database_url: str
    max_connection_count: int = 5
    min_connection_count: int = 5

    logging_level: int = logging.DEBUG
