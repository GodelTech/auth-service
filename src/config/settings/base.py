from enum import Enum

from pydantic import BaseSettings


class AppEnvTypes(Enum):
    prod: str = "production"
    dev: str = "development"
    test: str = "test"
    docker: str = "docker"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.dev

    # class Config:
    #     env_file = ".env"
