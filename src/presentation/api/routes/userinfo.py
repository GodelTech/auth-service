import logging
from typing import Any, Optional, Union

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi_cache.coder import JsonCoder
from fastapi_cache.decorator import cache

from src.business_logic.cache.key_builders import builder_with_parametr
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.userinfo import UserInfoServices
from src.config.settings.cache_time import CacheTimeSettings
from src.data_access.postgresql.errors.user import ClaimsNotFoundError
from src.di.providers import provide_userinfo_service_stub
from src.presentation.api.models.userinfo import ResponseUserInfoModel

logger = logging.getLogger(__name__)

userinfo_router = APIRouter(prefix="/userinfo", tags=["UserInfo"])


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
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
) -> dict[str, Any]:
    try:
        userinfo_class = userinfo_class
        token = request.headers.get("authorization") or auth_swagger
        userinfo_class.authorization = token
        logger.debug("Collecting Claims from DataBase.")
        result = await userinfo_class.get_user_info()

        return {k: v for k, v in result.items() if v is not None}

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for this claims",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Token"
        )


@userinfo_router.post("/", response_model=ResponseUserInfoModel)
@cache(
    expire=CacheTimeSettings.USERINFO,
    coder=JsonCoder,
    key_builder=builder_with_parametr,
)
async def post_userinfo(
    request: Request,
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),  # crutch for swagger
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
) -> dict[str, Any]:
    try:
        userinfo_class = userinfo_class
        token = request.headers.get("authorization") or auth_swagger
        userinfo_class.authorization = token
        logger.info("Collecting Claims from DataBase.")
        result = await userinfo_class.get_user_info()
        return {k: v for k, v in result.items() if v is not None}

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for this claims",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Token"
        )


@userinfo_router.get("/jwt", response_model=str)
@cache(
    expire=CacheTimeSettings.USERINFO_JWT,
    coder=JsonCoder,
    key_builder=builder_with_parametr,
)
async def get_userinfo_jwt(
    request: Request,
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
) -> str:
    try:
        userinfo_class = userinfo_class
        jwt_service = JWTService()
        token = request.headers.get("authorization") or auth_swagger
        userinfo_class.authorization = token
        logger.info("Collecting Claims from DataBase.")
        result = await userinfo_class.get_user_info()
        result = {k: v for k, v in result.items() if v is not None}
        return await userinfo_class.jwt.encode_jwt(payload=result)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Token"
        )

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for this claims",
        )


@userinfo_router.get("/get_default_token", response_model=str)
async def get_default_token(
    with_iss_me: Optional[bool] = None,
    with_aud: Optional[bool] = None,
    scope: str = "profile",
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
) -> str:
    try:
        uis = userinfo_class
        payload: dict[str, Any] = {"sub": "1", "scope": scope}
        if with_iss_me:
            payload["iss"] = "me"
        if with_aud:
            payload["aud"] = ["admin", "userinfo", "introspection", "revoke"]
        return await uis.jwt.encode_jwt(payload)
    except:
        raise HTTPException(status_code=500)


@userinfo_router.get("/decode_token", response_model=dict)
async def get_decode_token(
    token: str,
    issuer: Optional[str] = None,
    audience: Optional[str] = None,
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
) -> dict[str, Any]:
    uis = userinfo_class
    kwargs = {}
    if issuer is not None:
        kwargs["issuer"] = issuer
    if audience is not None:
        kwargs["audience"] = audience

    return await uis.jwt.decode_token(token, **kwargs)
