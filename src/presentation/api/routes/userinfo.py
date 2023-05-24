import logging
from typing import Any, Union

from fastapi import APIRouter, HTTPException, Header, Request, status, Depends
from fastapi_cache.coder import JsonCoder
from fastapi_cache.decorator import cache
from src.business_logic.services.userinfo import UserInfoServices
from src.config.settings.cache_time import CacheTimeSettings
from src.data_access.postgresql.errors.user import ClaimsNotFoundError
from src.data_access.postgresql.repositories import ClientRepository, PersistentGrantRepository, UserRepository
from src.presentation.api.models.userinfo import ResponseUserInfoModel
from src.presentation.middleware.authorization_validation import authorization_middleware

logger = logging.getLogger(__name__)

userinfo_router = APIRouter(
    prefix="/userinfo", 
    tags=["UserInfo"], 
    dependencies=[Depends(authorization_middleware)]
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
) -> dict[str, Any]:
    session = request.state.session
    userinfo_class = UserInfoServices(
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
) -> dict[str, Any]:
    session = request.state.session
    userinfo_class = UserInfoServices(
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
) -> str:
    session = request.state.session
    userinfo_class = UserInfoServices(
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

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for this claims",
        )