import logging

from src.config.settings.app import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True

    title: str = "Dev IS POC application"

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env"
