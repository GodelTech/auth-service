import logging
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status

from fastapi_cache.decorator import cache
from src.business_logic.cache.key_builders import builder_with_parametr
from fastapi_cache.coder import JsonCoder
from src.config.settings.cache_time import CacheTimeSettings

from src.business_logic.services.userinfo import UserInfoServices
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.errors.user import ClaimsNotFoundError
from src.presentation.api.models.userinfo import ResponseUserInfoModel


logger = logging.getLogger("is_app")

userinfo_router = APIRouter(
    prefix="/userinfo",
)


@userinfo_router.get(
    "/", response_model=ResponseUserInfoModel, tags=["UserInfo"]
)
@cache(
    expire=CacheTimeSettings.USERINFO,
    coder=JsonCoder,
    key_builder=builder_with_parametr,
)
async def get_userinfo(
    request: Request,
    auth_swagger: Union[str, None] = Header(default=None, description="Authorization"),  #crutch for swagger
    userinfo_class: UserInfoServices = Depends(),
):
    try:
        userinfo_class = userinfo_class
        token = request.headers.get('authorization')

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
            detail="You don't have permission for this claims"
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Incorrect Token"
        )

    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@userinfo_router.post(
    "/", response_model=ResponseUserInfoModel, tags=["UserInfo"]
)
@cache(
    expire=CacheTimeSettings.USERINFO,
    coder=JsonCoder,
    key_builder=builder_with_parametr,
)
async def post_userinfo(
    request: Request,
    auth_swagger: Union[str, None] = Header(default=None, description="Authorization"),  #crutch for swagger
    userinfo_class: UserInfoServices = Depends(),
):
    try:
        userinfo_class = userinfo_class
        token = request.headers.get('authorization')

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
            detail="You don't have permission for this claims"
        )
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Incorrect Token"
        )

    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@userinfo_router.get("/jwt", response_model=str, tags=["UserInfo"])
@cache(
    expire=CacheTimeSettings.USERINFO_JWT,
    coder=JsonCoder,
    key_builder=builder_with_parametr,
)
async def get_userinfo_jwt(
    request: Request,
    auth_swagger: Union[str, None] = Header(default=None, description="Authorization"),
    userinfo_class: UserInfoServices = Depends(),
):

    try:
        userinfo_class = userinfo_class
        jwt_service = JWTService()
        
        token = request.headers.get('authorization')

        if token != None:
            userinfo_class.authorization = token
        elif auth_swagger != None:
            userinfo_class.authorization = auth_swagger
        else:
            raise PermissionError

        logger.info("Collecting Claims from DataBase.")
        return await jwt_service.encode_jwt(payload = await userinfo_class.get_user_info())

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Incorrect Token"
        )

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You don't have permission for this claims"
        )

    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@userinfo_router.get(
    "/get_default_token", response_model=str, tags=["UserInfo"]
)
async def get_default_token():
    try:
        uis = UserInfoServices()
        return await uis.jwt.encode_jwt(payload={"sub": "1"})
    except:
        raise HTTPException(status_code=500)


@userinfo_router.get("/decode_token", response_model=dict, tags=["UserInfo"])
async def get_decode_token(token: str):
    try:
        uis = UserInfoServices()
        return await uis.jwt.decode_token(token)
    except:
        raise HTTPException(status_code=500)
