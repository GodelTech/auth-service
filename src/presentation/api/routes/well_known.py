from fastapi import APIRouter, Depends, HTTPException, Request
from src.business_logic.services.well_known import WellKnownServies
from src.presentation.api.models.well_known import ResponseOpenIdConfiguration
from fastapi_cache.decorator import cache
from src.config.settings.cache_time import CacheTimeSettings
import logging

well_known_router = APIRouter(
    prefix='/.well-known',
)

logger = logging.getLogger('is_app')


@well_known_router.get('/openid-configuration', response_model=ResponseOpenIdConfiguration, tags=['Well Known'])
async def get_openid_configuration(request: Request, well_known_info_class: WellKnownServies = Depends()):
     try:
          logger.info('Collecting Data for OpenID Configuration.')
          well_known_info_class = well_known_info_class
          well_known_info_class.request = request
          return await well_known_info_class.get_openid_configuration()
     except:
          raise HTTPException(status_code=404)
