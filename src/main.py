import os
from logging.config import dictConfig
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config import LogConfig, get_app_settings
from src.config.settings.development import DevAppSettings
from src.presentation.api import router
from src.di import Container


def get_application(test=False) -> FastAPI:
    # configure logging
    dictConfig(LogConfig().to_dict)

    container = Container()
    settings = container.config()

    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    container.db()

    application.container = container

    application.include_router(router)
    return application


app = get_application()
