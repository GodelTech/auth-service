import logging
from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    status,
    Depends
)
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from src.business_logic.services import ScopeService
from src.business_logic.services.well_known import WellKnownServices
from src.config.settings.cache_time import CacheTimeSettings
from src.data_access.postgresql.repositories import WellKnownRepository, ResourcesRepository
from src.presentation.api.models.well_known import (
    ResponseJWKS,
    ResponseOpenIdConfiguration,
)
from src.di.providers import provide_async_session_stub

well_known_router = APIRouter(prefix="/.well-known", tags=["Well Known"])

logger = logging.getLogger(__name__)


@well_known_router.get(
    "/openid-configuration", response_model=ResponseOpenIdConfiguration
)
@cache(expire=CacheTimeSettings.WELL_KNOWN_OPENID_CONFIG)
async def get_openid_configuration(
    request: Request,
    session: AsyncSession = Depends(provide_async_session_stub)
) -> dict[str, Any]:
    try:
        logger.debug("Collecting Data for OpenID Configuration.")
        well_known_info_class = WellKnownServices(
            session=session, 
            wlk_repo=WellKnownRepository(session),
            scope_service=ScopeService(
                resource_repo=ResourcesRepository(session),
                session=session
            ),
        )
        well_known_info_class.request = request
        result = await well_known_info_class.get_openid_configuration()
        return {k: v for k, v in result.items() if v is not None}
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@well_known_router.get("/jwks", response_model=ResponseJWKS)
async def get_jwks(
    request: Request,
) -> dict[str, Any]:
    try:
        session = "no_session"
        well_known_info_class = WellKnownServices(
            session=session, wlk_repo=WellKnownRepository(session),
        )
        well_known_info_class.request = request
        return {
            "keys": [
                await well_known_info_class.get_jwks(),
            ]
        }
    except:
        raise  # HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
