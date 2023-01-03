import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi_cache.decorator import cache

from src.business_logic.cache.key_builders import builder_with_parametr
from src.business_logic.services.well_known import WellKnownServies
from src.config.settings.cache_time import CacheTimeSettings
from src.presentation.api.models.well_known import ResponseOpenIdConfiguration

well_known_router = APIRouter(
    prefix="/.well-known",
)

logger = logging.getLogger("is_app")


@well_known_router.get(
    "/openid-configuration",
    response_model=ResponseOpenIdConfiguration,
    tags=["Well Known"],
)
@cache(
    expire=CacheTimeSettings.WELL_KNOWN_OPENID_CONFIG,
    key_builder=builder_with_parametr,
)
async def get_openid_configuration(
    request: Request, well_known_info_class: WellKnownServies = Depends()
):
    try:
        logger.info("Collecting Data for OpenID Configuration.")
        well_known_info_class = well_known_info_class
        well_known_info_class.request = request
        return await well_known_info_class.get_openid_configuration()
    except:
        raise HTTPException(status_code=404)
