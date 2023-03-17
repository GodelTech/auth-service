import logging
import os
from pydantic import PostgresDsn
from typing import Union
from src.config.settings.app import AppSettings


class TestAppSettings(AppSettings):
    debug: bool = True

    title: str = "Test IS POC application"

    database_url:PostgresDsn
    max_connection_count: int = 5
    min_connection_count: int = 5

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = os.path.join(os.getcwd(), "envfiles/.env.test")
