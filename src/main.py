from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config import get_app_settings
from src.config.events import create_start_app_handler, create_stop_app_handler
from src.presentation.api import router


def get_application() -> FastAPI:
    settings = get_app_settings()

    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler(
        "startup",
        create_start_app_handler(application, settings),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application),
    )

    return application


app = get_application()
app.include_router(router)
