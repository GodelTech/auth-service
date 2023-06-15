import logging
from logging.config import dictConfig
from typing import Optional, Any
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.staticfiles import StaticFiles
from redis import asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.presentation.api.exception_handlers import exception_handler_mapping
from src.presentation.middleware.https_global_middleware import (
    HttpsGlobalMiddleware,
)
from src.presentation.api import router
from src.di import Container
from src.dyna_config import (
    DB_MAX_CONNECTION_COUNT,
    DB_URL,
    REDIS_URL,
)

import src.presentation.admin_ui.controllers as ui
import src.di.providers as prov
import logging
from src.log import LOGGING_CONFIG
from src.data_access.postgresql.repositories import UserRepository
from src.business_logic.services.admin_auth import AdminAuthService

logger = logging.getLogger(__name__)


class NewFastApi(FastAPI):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.container: Optional[Container] = None


def get_application(test: bool = False) -> NewFastApi:
    # configure logging
    dictConfig(LOGGING_CONFIG)

    origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    application = NewFastApi()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application = setup_exception_handlers(application)

    application = setup_exception_handlers(application)
    setup_di(application)
    container = Container()
    container.db()
    application.container = container

    application.include_router(router)
    application.mount(
        "/static",
        StaticFiles(directory="src/presentation/api/templates/static"),
        name="static",
    )

    return application


# TODO: move the creation of RSA keys here.
def setup_di(app: FastAPI) -> None:
    db_engine = prov.provide_db(
        database_url=DB_URL, max_connection_count=DB_MAX_CONNECTION_COUNT
    )

    db = prov.provide_db_only(
        database_url=DB_URL, max_connection_count=DB_MAX_CONNECTION_COUNT
    )
    session = prov.ProviderSession(db.session_factory)

    app.dependency_overrides[
        prov.provide_async_session_stub
    ] = session

    app.add_middleware(middleware_class=HttpsGlobalMiddleware)
    
    #Register admin-ui controllers on application start-up.
    admin = ui.CustomAdmin(
        app,
        db_engine,
        templates_dir="src/presentation/admin_ui/controllers/templates",
        authentication_backend=ui.AdminAuthController(
            secret_key="1234",
            auth_service=AdminAuthService(
                user_repo=UserRepository(
                    session=prov.provide_async_session(db_engine)
                ),
            ),
        ),
    )

    # Identity Resourses
    admin.add_view(ui.IdentityProviderAdminController)
    admin.add_view(ui.IdentityProviderMappedAdminController)
    admin.add_view(ui.IdentityResourceAdminController)
    admin.add_view(ui.IdentityClaimAdminController)
    admin.add_base_view(ui.SeparationLine)

    # Client 
    admin.add_view(ui.ClientAdminController)
    admin.add_view(ui.ResponseTypeAdminController)
    admin.add_view(ui.ClientScopeController)
    admin.add_view(ui.AccessTokenTypeAdminController)
    admin.add_view(ui.ProtocolTypeController)
    admin.add_view(ui.RefreshTokenUsageTypeController)
    admin.add_view(ui.RefreshTokenExpirationTypeController)
    admin.add_view(ui.ClientSecretController)
    admin.add_view(ui.ClientRedirectUriController)
    admin.add_view(ui.ClientCorsOriginController)
    admin.add_view(ui.ClientPostLogoutRedirectUriController)
    admin.add_view(ui.ClientClaimController)
    admin.add_view(ui.ClientIdRestrictionController)
    admin.add_view(ui.DeviceAdminController)
    admin.add_base_view(ui.SeparationLine)

    # User/UserClaim

    admin.add_view(ui.UserAdminController)
    admin.add_view(ui.PasswordAdminController)
    admin.add_view(ui.UserClaimAdminController)
    admin.add_view(ui.TypesUserClaimAdminController)
    admin.add_base_view(ui.SeparationLine)

    # Other
    admin.add_view(ui.RoleAdminController)
    admin.add_view(ui.GroupAdminController)
    admin.add_view(ui.PermissionAdminController)
    admin.add_base_view(ui.SeparationLine)

    # Grants
    admin.add_view(ui.PersistentGrantAdminController)
    admin.add_view(ui.PersistentGrantTypeAdminController)
    admin.add_base_view(ui.SeparationLine)

    # ApiResourses
    admin.add_view(ui.ApiResourceAdminController)
    admin.add_view(ui.ApiSecretAdminController)
    admin.add_view(ui.ApiSecretTypeAdminController)
    admin.add_view(ui.ApiClaimAdminController)
    admin.add_view(ui.ApiClaimTypeAdminController)
    admin.add_view(ui.ApiScopeAdminController)
    admin.add_view(ui.ApiScopeClaimAdminController)
    admin.add_view(ui.ApiScopeClaimTypeAdminController)
    admin.add_base_view(ui.SeparationLine)


def setup_exception_handlers(app: FastAPI) -> FastAPI:
    for exception, handler in exception_handler_mapping.items():
        app.add_exception_handler(exception, handler)
    return app


app = get_application()


# expose the default Python metrics to the /metrics endpoint
Instrumentator().instrument(app).expose(app)


# Redis activation
@app.on_event("startup")
async def startup() -> None:
    logger.info("Creating Redis connection with DataBase.")
    redis = aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Created Redis connection with DataBase.")
