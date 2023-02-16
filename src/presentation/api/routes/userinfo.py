import logging
from typing import Union

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi_cache.coder import JsonCoder
from fastapi_cache.decorator import cache

from src.business_logic.cache.key_builders import builder_with_parameter
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.userinfo import UserInfoServices
from src.config.settings.cache_time import CacheTimeSettings
from src.data_access.postgresql.errors.user import ClaimsNotFoundError
from src.di.providers import provide_userinfo_service_stub
from src.presentation.api.models.userinfo import ResponseUserInfoModel

logger = logging.getLogger(__name__)

userinfo_router = APIRouter(
    prefix="/userinfo",
)


@userinfo_router.get(
    "/", response_model=ResponseUserInfoModel, tags=["UserInfo"]
)
@cache(
    expire=CacheTimeSettings.USERINFO,
    coder=JsonCoder,
    key_builder=builder_with_parameter,
)
async def get_userinfo(
    request: Request,
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),  # crutch for swagger
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
):
    try:
        userinfo_class = userinfo_class
        token = request.headers.get("authorization")

        if token != None:
            userinfo_class.authorization = token
        elif auth_swagger != None:
            userinfo_class.authorization = auth_swagger
        else:
            raise PermissionError

        logger.info("Collecting Claims from DataBase.")
        return await userinfo_class.get_user_info()

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for this claims",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Token"
        )

    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@userinfo_router.post(
    "/", response_model=ResponseUserInfoModel, tags=["UserInfo"]
)
@cache(
    expire=CacheTimeSettings.USERINFO,
    coder=JsonCoder,
    key_builder=builder_with_parameter,
)
async def post_userinfo(
    request: Request,
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),  # crutch for swagger
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
):
    try:
        userinfo_class = userinfo_class
        token = request.headers.get("authorization")

        if token != None:
            userinfo_class.authorization = token
        elif auth_swagger != None:
            userinfo_class.authorization = auth_swagger
        else:
            raise PermissionError

        logger.info("Collecting Claims from DataBase.")
        return await userinfo_class.get_user_info()

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for this claims",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Token"
        )

    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@userinfo_router.get("/jwt", response_model=str, tags=["UserInfo"])
@cache(
    expire=CacheTimeSettings.USERINFO_JWT,
    coder=JsonCoder,
    key_builder=builder_with_parameter,
)
async def get_userinfo_jwt(
    request: Request,
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
):
    try:
        userinfo_class = userinfo_class
        jwt_service = JWTService()

        token = request.headers.get("authorization")
        if token != None:
            userinfo_class.authorization = token
        elif auth_swagger != None:
            userinfo_class.authorization = auth_swagger
        else:
            raise PermissionError

        logger.info("Collecting Claims from DataBase.")
        return await userinfo_class.jwt.encode_jwt(
            payload=await userinfo_class.get_user_info()
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Token"
        )

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for this claims",
        )

    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@userinfo_router.get(
    "/get_default_token", response_model=str, tags=["UserInfo"]
)
async def get_default_token(
    with_iss_me: bool = None,
    with_aud_facebook: bool = None,
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
):
    try:
        uis = userinfo_class
        payload = {"sub": "1"}
        if with_iss_me:
            payload["iss"] = "me"
        if with_aud_facebook:
            payload["aud"] = ["facebook"]
        return await uis.jwt.encode_jwt(payload)
    except:
        raise HTTPException(status_code=500)


@userinfo_router.get("/decode_token", response_model=dict, tags=["UserInfo"])
async def get_decode_token(
    token: str,
    issuer: str = None,
    audience: str = None,
    userinfo_class: UserInfoServices = Depends(provide_userinfo_service_stub),
):
    # try:
    uis = userinfo_class
    kwargs = {}
    if issuer is not None:
        kwargs["issuer"] = issuer
    if audience is not None:
        kwargs["audience"] = audience

    return await uis.jwt.decode_token(token, **kwargs)
    # except:
    raise HTTPException(status_code=500)
