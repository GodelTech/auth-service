import logging
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status

from fastapi_cache.decorator import cache
from src.business_logic.cache.key_builders import builder_with_parametr
from fastapi_cache.coder import JsonCoder
from src.config.settings.cache_time import CacheTimeSettings

from src.business_logic.services.userinfo import UserInfoServies

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
    auth_swagger: str | None = Header(default=None, description="Authorization"),  #crutch for swagger
    userinfo_class: UserInfoServies = Depends(),
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Claims for user you are looking for does not exist",
        )

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect Authorization Token"
        )
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
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
    auth_swagger: str | None = Header(default=None, description="Authorization"),
    userinfo_class: UserInfoServies = Depends(),
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Claims for user you are looking for does not exist",
        )

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect Authorization Token"
        )
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
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
    auth_swagger: str | None = Header(default=None, description="Authorization"),
    userinfo_class: UserInfoServies = Depends(),
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
            
        result = await userinfo_class.get_user_info_jwt()
        return result

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Claims for user you are looking for does not exist",
        )

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect Authorization Token"
        )
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect Token"
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
        uis = UserInfoServies()
        uis.jwt.set_expire_time(expire_hours=1)
        return uis.jwt.encode_jwt(payload={"sub": "1"})
    except:
        raise HTTPException(status_code=500)


@userinfo_router.get("/decode_token", response_model=dict, tags=["UserInfo"])
async def get_decode_token(token: str):
    try:
        uis = UserInfoServies()
        return uis.jwt.decode_token(token)
    except:
        raise HTTPException(status_code=500)
