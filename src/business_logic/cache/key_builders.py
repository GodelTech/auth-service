from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from src.config.settings.cache_time import CacheTimeSettings
from typing import Optional
from fastapi import Request, Response
# import logging
# import redis

# logger = logging.getLogger('is_app')

def builder_with_parametr(
        func,
        namespace: Optional[str] = "",
        request: Request = None,
        response: Response = None,
        *args,
        **kwargs,
):
    prefix = f'client-{request.client.host}'
    cache_key = f"{prefix}:{func.__module__}:{func.__name__}:{request.query_params}"
    
    # r = redis.StrictRedis(host='localhost', port=6379, db=0)
    # if r.get(cache_key):
    #     logger.info(f'Used old Redis Key: "{cache_key}"')
    # else:
    #     logger.info(f'New Redis Key: "{cache_key}"  ')
    return cache_key