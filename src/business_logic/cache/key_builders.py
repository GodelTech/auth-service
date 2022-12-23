from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from src.config.settings.cache_time import CacheTimeSettings
from typing import Optional
from fastapi import Request, Response


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
    return cache_key