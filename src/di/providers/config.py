from src.config import get_app_settings
from src.config.settings.base import BaseAppSettings


def provide_config_stub():
    ...


def provide_config() -> BaseAppSettings:
    return get_app_settings()
