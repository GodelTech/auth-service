import logging
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware

from src.presentation.api.middleware.authorization_validation import AuthorizationMiddleware
from src.config import LogConfig
from src.di import Container
from src.presentation.api import router


logger = logging.getLogger("is_app")


def get_application(test=False) -> FastAPI:
    # configure logging
    dictConfig(LogConfig().to_dict)

    container = Container()
    settings = container.config()

    application = FastAPI(**settings.fastapi_kwargs)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(AuthorizationMiddleware)
    
    
    container.db()
    application.container = container

    application.include_router(router)
    
    return application


app = get_application()


LOCAL_REDIS_URL = "redis://127.0.0.1:6379"  # move to .env file


# Redis activation
@app.on_event("startup")
async def startup():
    logger.info("Creating Redis connection with DataBase.")
    redis = aioredis.from_url(
        LOCAL_REDIS_URL, encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Created Redis connection with DataBase.")
