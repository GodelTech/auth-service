import logging
import time
from typing import Optional, Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi_cache.decorator import cache

from src.business_logic.cache.key_builders import builder_with_parametr
from src.business_logic.services.well_known import WellKnownServies
from src.config.settings.cache_time import CacheTimeSettings
from src.presentation.api.models.well_known import (
    ResponseJWKS,
    ResponseOpenIdConfiguration,
)

well_known_router = APIRouter(prefix="/.well-known", tags=["Well Known"])

logger = logging.getLogger(__name__)


@well_known_router.get(
    "/openid-configuration", response_model=ResponseOpenIdConfiguration
)
@cache(
    expire=CacheTimeSettings.WELL_KNOWN_OPENID_CONFIG,
    # key_builder=builder_with_parametr,
)
async def get_openid_configuration(
    request: Request, well_known_info_class: WellKnownServies = Depends()
) -> dict[str, Any]:
    try:
        logger.info("Collecting Data for OpenID Configuration.")
        well_known_info_class = well_known_info_class
        well_known_info_class.request = request
        return await well_known_info_class.get_openid_configuration()
    except:
        raise HTTPException(status_code=404)


@well_known_router.get("/jwks", response_model=ResponseJWKS)
async def get_jwks(
    request: Request, well_known_info_class: WellKnownServies = Depends()
) -> dict[str, Any]:
    try:
        logger.info("JWKS")
        well_known_info_class = well_known_info_class
        well_known_info_class.request = request
        return {
            "keys": [
                await well_known_info_class.get_jwks(),
            ]
        }
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
