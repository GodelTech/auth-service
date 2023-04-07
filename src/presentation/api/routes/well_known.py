import logging
from typing import Dict, Any
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi_cache.decorator import cache
from fastapi.responses import JSONResponse
from src.business_logic.cache.key_builders import builder_with_parametr
from src.business_logic.services.well_known import WellKnownServices
from src.config.settings.cache_time import CacheTimeSettings
from src.presentation.api.models.well_known import (
    ResponseJWKS,
    ResponseOpenIdConfiguration,
)
from src.di.providers.services import provide_wellknown_service_stub

well_known_router = APIRouter(prefix="/.well-known", tags=["Well Known"])

logger = logging.getLogger(__name__)


@well_known_router.get(
    "/openid-configuration", response_model=ResponseOpenIdConfiguration
)
@cache(expire=CacheTimeSettings.WELL_KNOWN_OPENID_CONFIG)
async def get_openid_configuration(
    request: Request,
    well_known_info_class: WellKnownServices = Depends(
        provide_wellknown_service_stub
    ),
) -> Dict[str, Any]:
    try:
        logger.info("Collecting Data for OpenID Configuration.")
        well_known_info_class = well_known_info_class
        well_known_info_class.request = request
        result = await well_known_info_class.get_openid_configuration()
        result_dict = {k: v for k, v in result.items() if v is not None}
        # What headers to return
        return JSONResponse(content=result_dict)
    except Exception as exception:
        logger.exception(exception)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@well_known_router.get("/jwks", response_model=ResponseJWKS)
async def get_jwks(
    request: Request,
    well_known_info_class: WellKnownServices = Depends(
        provide_wellknown_service_stub
    ),
) -> Dict[str, Any]:
    try:
        logger.info("JWKS")
        well_known_info_class = well_known_info_class
        well_known_info_class.request = request
        keys_dict = {
            "keys": [
                await well_known_info_class.get_jwks(),
            ]
        }
        # What headers to return
        return JSONResponse(content=keys_dict)
    except Exception as exception:
        logger.exception(exception)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
