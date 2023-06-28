import logging
from typing import Any, Union

from fastapi import APIRouter, Header, Request, Depends
from fastapi_cache.coder import JsonCoder
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.userinfo import UserInfoService
from src.config.settings.cache_time import CacheTimeSettings
from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository,
)
from src.presentation.api.models.userinfo import ResponseUserInfoModel
from src.presentation.middleware.authorization_validation import (
    authorization_middleware,
)
from src.di.providers import provide_async_session_stub

logger = logging.getLogger(__name__)

userinfo_router = APIRouter(
    prefix="/userinfo",
    tags=["UserInfo"],
    dependencies=[Depends(authorization_middleware)],
)


@userinfo_router.get("/", response_model=dict)
@cache(
    expire=CacheTimeSettings.USERINFO,
    coder=JsonCoder,
    # key_builder=builder_with_parametr,
)
async def get_userinfo(
    request: Request,
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),  # crutch for swagger
    session: AsyncSession = Depends(provide_async_session_stub),
) -> dict[str, Any]:
    userinfo_class = UserInfoService(
        session=session,
        user_repo=UserRepository(session),
        client_repo=ClientRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
    )
    token = request.headers.get("authorization") or auth_swagger
    userinfo_class.authorization = token
    logger.debug("Collecting Claims from DataBase.")
    result = await userinfo_class.get_user_info()
    result = {k: v for k, v in result.items() if v is not None}
    return result


@userinfo_router.post("/", response_model=ResponseUserInfoModel)
# @cache(
#     expire=CacheTimeSettings.USERINFO,
#     coder=JsonCoder,
#    # key_builder=builder_with_parametr,
# )
async def post_userinfo(
    request: Request,
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),  # crutch for swagger
    session: AsyncSession = Depends(provide_async_session_stub),
) -> dict[str, Any]:
    userinfo_class = UserInfoService(
        session=session,
        user_repo=UserRepository(session),
        client_repo=ClientRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
    )
    token = request.headers.get("authorization") or auth_swagger
    userinfo_class.authorization = token
    logger.info("Collecting Claims from DataBase.")
    result = await userinfo_class.get_user_info()
    return {k: v for k, v in result.items() if v is not None}


@userinfo_router.get("/jwt", response_model=str)
@cache(
    expire=CacheTimeSettings.USERINFO_JWT,
    coder=JsonCoder,
    # key_builder=builder_with_parametr,
)
async def get_userinfo_jwt(
    request: Request,
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),
    session: AsyncSession = Depends(provide_async_session_stub),
) -> str:
    userinfo_class = UserInfoService(
        session=session,
        user_repo=UserRepository(session),
        client_repo=ClientRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
    )
    token = request.headers.get("authorization") or auth_swagger
    userinfo_class.authorization = token
    logger.info("Collecting Claims from DataBase.")
    result = await userinfo_class.get_user_info()
    result = {k: v for k, v in result.items() if v is not None}
    return await userinfo_class.jwt.encode_jwt(payload=result)
