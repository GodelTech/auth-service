import logging
from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    status,
)
from fastapi_cache.decorator import cache

from src.business_logic.services.well_known import WellKnownServices
from src.config.settings.cache_time import CacheTimeSettings
from src.data_access.postgresql.repositories import WellKnownRepository
from src.presentation.api.models.well_known import (
    ResponseJWKS,
    ResponseOpenIdConfiguration,
)

well_known_router = APIRouter(prefix="/.well-known", tags=["Well Known"])

logger = logging.getLogger(__name__)


@well_known_router.get("/openid-configuration", response_model=ResponseOpenIdConfiguration)
@cache(expire=CacheTimeSettings.WELL_KNOWN_OPENID_CONFIG)
async def get_openid_configuration(
        request: Request,
) -> dict[str, Any]:
    try:
        session = request.state.session
        logger.debug("Collecting Data for OpenID Configuration.")
        well_known_info_class = WellKnownServices(
            session=session,
            wlk_repo=WellKnownRepository(session)
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
        logger.debug("JWKS")
        session = request.state.session
        well_known_info_class = WellKnownServices(
            session=session,
            wlk_repo=WellKnownRepository(session)
        )
        well_known_info_class.request = request
        return {
            "keys": [
                await well_known_info_class.get_jwks(),
            ]
        }
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
