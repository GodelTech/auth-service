import logging
from logging.config import dictConfig
from typing import Optional, Any
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.staticfiles import StaticFiles
from httpx import AsyncClient
from redis import asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware

from src.presentation.api.middleware.authorization_validation import (
    AuthorizationMiddleware,
)
from src.presentation.api.middleware.access_token_validation import (
    AccessTokenMiddleware,
)
from src.presentation.api import router
from src.di import Container
from src.dyna_config import DB_MAX_CONNECTION_COUNT, DB_URL, REDIS_URL
import src.presentation.admin_ui.controllers as ui
import src.di.providers as prov
   
import logging
from src.log import LOGGING_CONFIG
from fastapi_utils.tasks import repeat_every

logger = logging.getLogger(__name__)


class NewFastApi(FastAPI):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.container: Optional[Container] = None


def get_application(test: bool = False) -> NewFastApi:
    # configure logging
    dictConfig(LOGGING_CONFIG)

    application = NewFastApi()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


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
    
    app.add_middleware(
        middleware_class=AuthorizationMiddleware, 
        blacklisted_repo=prov.provide_blacklisted_repo(db_engine)
    )
    app.add_middleware(
        middleware_class=AccessTokenMiddleware, 
        blacklisted_repo=prov.provide_blacklisted_repo(db_engine)
    )

    from src.data_access.postgresql.repositories.blacklisted_token import BlacklistedTokenRepository
    
    app.add_middleware(AuthorizationMiddleware)
    app.add_middleware(middleware_class=AccessTokenMiddleware, blacklisted_repo=BlacklistedTokenRepository(db_engine))

    # Register admin-ui controllers on application start-up.
    admin = ui.CustomAdmin(
        app,
        db_engine,
        templates_dir="templates_admin_ui",
        authentication_backend=ui.AdminAuthController(
            secret_key="1234",
            auth_service=prov.provide_admin_auth_service(
                user_repo=prov.provide_user_repo(db_engine),
                password_service=prov.provide_password_service(),
                jwt_service=prov.provide_jwt_service(),
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
    admin.add_view(ui.AccessTokenTypeAdminController)
    admin.add_view(ui.ProtocolTypeController)
    admin.add_view(ui.RefreshTokenUsageTypeController)
    admin.add_view(ui.RefreshTokenExpirationTypeController)
    admin.add_view(ui.ClientSecretController)
    admin.add_view(ui.ClientGrantTypeController)
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

    nodepends_provide_auth_service = lambda:prov.provide_auth_service(
        client_repo=prov.provide_client_repo(db_engine),
        user_repo=prov.provide_user_repo(db_engine),
        persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
        device_repo=prov.provide_device_repo(db_engine),
        password_service=prov.provide_password_service(),
        jwt_service=prov.provide_jwt_service(),
    )
    app.dependency_overrides[
       prov.provide_auth_service_stub
    ] = nodepends_provide_auth_service

    nodepends_provide_endsession_servise = lambda:prov.provide_endsession_service(
        client_repo=prov.provide_client_repo(db_engine),
        persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
        jwt_service=prov.provide_jwt_service(),
    )
    app.dependency_overrides[
       prov.provide_endsession_service_stub
    ] = nodepends_provide_endsession_servise

    nodepends_provide_introspection_service = (
        lambda:prov.provide_introspection_service(
            jwt=prov.provide_jwt_service(),
            user_repo=prov.provide_user_repo(db_engine),
            client_repo=prov.provide_client_repo(db_engine),
            persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
        )
    )
    app.dependency_overrides[
       prov.provide_introspection_service_stub
    ] = nodepends_provide_introspection_service

    nodepends_provide_token_service = lambda:prov.provide_token_service(
        jwt_service=prov.provide_jwt_service(),
        user_repo=prov.provide_user_repo(db_engine),
        client_repo=prov.provide_client_repo(db_engine),
        persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
        device_repo=prov.provide_device_repo(db_engine),
        blacklisted_repo=prov.provide_blacklisted_repo(db_engine)
    )
    app.dependency_overrides[
       prov.provide_token_service_stub
    ] = nodepends_provide_token_service

    nodepends_provide_userinfo_service = lambda:prov.provide_userinfo_service(
        jwt=prov.provide_jwt_service(),
        user_repo=prov.provide_user_repo(db_engine),
        client_repo=prov.provide_client_repo(db_engine),
        persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
    )
    app.dependency_overrides[
       prov.provide_userinfo_service_stub
    ] = nodepends_provide_userinfo_service

    nodepends_provide_login_form_service = lambda:prov.provide_login_form_service(
        client_repo=prov.provide_client_repo(db_engine),
        oidc_repo=prov.provide_third_party_oidc_repo(db_engine),
    )

    app.dependency_overrides[
       prov.provide_login_form_service_stub
    ] = nodepends_provide_login_form_service

    nodepends_provide_admin_user_service = lambda:prov.provide_admin_user_service(
        user_repo=prov.provide_user_repo(db_engine),
    )

    app.dependency_overrides[
       prov.provide_admin_user_service_stub
    ] = nodepends_provide_admin_user_service

    nodepends_provide_admin_group_service = lambda:prov.provide_admin_group_service(
        group_repo=prov.provide_group_repo(db_engine),
    )

    app.dependency_overrides[
       prov.provide_admin_group_service_stub
    ] = nodepends_provide_admin_group_service

    nodepends_provide_admin_role_service = lambda:prov.provide_admin_role_service(
        role_repo=prov.provide_role_repo(db_engine),
    )
    app.dependency_overrides[
       prov.provide_admin_role_service_stub
    ] = nodepends_provide_admin_role_service

    nodepends_provide_device_service = lambda:prov.provide_device_service(
        client_repo=prov.provide_client_repo(db_engine),
        device_repo=prov.provide_device_repo(db_engine),
    )
    app.dependency_overrides[
       prov.provide_device_service_stub
    ] = nodepends_provide_device_service

    nodepends_provide_auth_third_party_oidc_service = (
        lambda:prov.provide_auth_third_party_oidc_service(
            client_repo=prov.provide_client_repo(db_engine),
            user_repo=prov.provide_user_repo(db_engine),
            persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
            oidc_repo=prov.provide_third_party_oidc_repo(db_engine),
            http_client=AsyncClient(),
        )
    )
    app.dependency_overrides[
       prov.provide_auth_third_party_oidc_service_stub
    ] = nodepends_provide_auth_third_party_oidc_service

    nodepends_provide_auth_linkedin_third_party_service = (
        lambda:prov.provide_auth_third_party_linkedin_service(
            client_repo=prov.provide_client_repo(db_engine),
            user_repo=prov.provide_user_repo(db_engine),
            persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
            oidc_repo=prov.provide_third_party_oidc_repo(db_engine),
            http_client=AsyncClient(),
        )
    )
    app.dependency_overrides[
       prov.provide_auth_third_party_linkedin_service_stub
    ] = nodepends_provide_auth_linkedin_third_party_service

    nodepends_provide_third_party_google_service = (
        lambda:prov.provide_third_party_google_service(
            client_repo=prov.provide_client_repo(db_engine),
            user_repo=prov.provide_user_repo(db_engine),
            persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
            oidc_repo=prov.provide_third_party_oidc_repo(db_engine),
            http_client=AsyncClient(),
        )
    )

    app.dependency_overrides[
       prov.provide_third_party_google_service_stub
    ] = nodepends_provide_third_party_google_service

    nodepends_provide_third_party_facebook_service = (
        lambda:prov.provide_third_party_facebook_service(
            client_repo=prov.provide_client_repo(db_engine),
            user_repo=prov.provide_user_repo(db_engine),
            persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
            oidc_repo=prov.provide_third_party_oidc_repo(db_engine),
            http_client=AsyncClient(),
        )
    )

    app.dependency_overrides[
       prov.provide_third_party_facebook_service_stub
    ] = nodepends_provide_third_party_facebook_service

    nodepends_provide_third_party_gitlab_service = (
        lambda:prov.provide_third_party_gitlab_service(
            client_repo=prov.provide_client_repo(db_engine),
            user_repo=prov.provide_user_repo(db_engine),
            persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
            oidc_repo=prov.provide_third_party_oidc_repo(db_engine),
            http_client=AsyncClient(),
        )
    )

    app.dependency_overrides[
       prov.provide_third_party_gitlab_service_stub
    ] = nodepends_provide_third_party_gitlab_service
    
    nodepends_wellknown_service = lambda:prov.provide_wellknown_service(
        wlk_repo=prov.provide_wellknown_repo(db_engine),
    )
    app.dependency_overrides[
       prov.provide_wellknown_service_stub
    ] = nodepends_wellknown_service

    nodepends_provide_third_party_microsoft_service = (
        lambda:prov.provide_third_party_microsoft_service(
            client_repo=prov.provide_client_repo(db_engine),
            user_repo=prov.provide_user_repo(db_engine),
            persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
            oidc_repo=prov.provide_third_party_oidc_repo(db_engine),
            http_client=AsyncClient(),
        )
    )

    app.dependency_overrides[
       prov.provide_third_party_microsoft_service_stub
    ] = nodepends_provide_third_party_microsoft_service

    nodepends_provide_third_party_microsoft_service = (
        lambda:prov.provide_third_party_microsoft_service(
            client_repo=prov.provide_client_repo(db_engine),
            user_repo=prov.provide_user_repo(db_engine),
            persistent_grant_repo=prov.provide_persistent_grant_repo(db_engine),
            oidc_repo=prov.provide_third_party_oidc_repo(db_engine),
            http_client=AsyncClient(),
        )
    )

    app.dependency_overrides[
       prov.provide_third_party_microsoft_service_stub
    ] = nodepends_provide_third_party_microsoft_service


app = get_application()


# TODO: Move this code to setup_di() function.
LOCAL_REDIS_URL = "redis://127.0.0.1:6379"  # move to .env file


# Redis activation
@app.on_event("startup")
async def startup() -> None:
    logger.info("Creating Redis connection with DataBase.")
    redis = aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Created Redis connection with DataBase.")


from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository

@app.on_event("startup")
@repeat_every(seconds=10 * 60)
async def remove_expired_tokens_task() -> None:
    logger.info("Started to remove expired tokens")
    db_engine = provide_db(
        database_url=DB_URL, max_connection_count=DB_MAX_CONNECTION_COUNT
    )
    token_class: PersistentGrantRepository = PersistentGrantRepository(db_engine)
    try:
        await token_class.delete_expired()
    except:
        logger.error("Removing of grants doesn't work")
