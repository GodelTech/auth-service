import logging
from typing import Any, Dict, List, Tuple

from pydantic import PostgresDsn

from src.config.settings.base import BaseAppSettings


class AppSettings(BaseAppSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "IS POC application"
    version: str = "0.1.0"

    database_url: PostgresDsn
    max_connection_count: int = 10

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }
