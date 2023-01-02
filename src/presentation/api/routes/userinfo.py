from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import Optional
from src.business_logic.services.userinfo import UserInfoServies
from src.presentation.api.models.userinfo import ResponseUserInfoModel, RequestUserInfoModel
from fastapi_cache.decorator import cache
from fastapi_cache.coder import JsonCoder 
from src.data_access.postgresql.errors.user import ClaimsNotFoundError
from src.config.settings.cache_time import CacheTimeSettings
from src.business_logic.cache.key_builders import builder_with_parametr
import logging

logger = logging.getLogger('is_app')

userinfo_router = APIRouter(
    prefix='/userinfo',
)


@userinfo_router.get('/', response_model=ResponseUserInfoModel, tags=['UserInfo'])
@cache(expire= CacheTimeSettings.USERINFO, coder= JsonCoder, key_builder=builder_with_parametr)
async def get_userinfo(request: Request, request_model: RequestUserInfoModel = Depends(), userinfo_class: UserInfoServies = Depends()):
    try:
        userinfo_class = userinfo_class
        userinfo_class.request = request_model
        logger.info('Collecting Claims from DataBase.')
        return await userinfo_class.get_user_info()

    except ClaimsNotFoundError:
        raise HTTPException(status_code=422, detail="Claims for user you are looking for does not exist")
        
    except:
        raise HTTPException(status_code=403, detail="Incorrect Token")


@userinfo_router.get('/jwt', response_model=str, tags=['UserInfo'])
@cache(expire= CacheTimeSettings.USERINFO_JWT, coder= JsonCoder, key_builder=builder_with_parametr)
async def get_userinfo_jwt(request_model: RequestUserInfoModel = Depends(), userinfo_class: UserInfoServies = Depends()):
    try:
        userinfo_class = userinfo_class
        userinfo_class.request = request_model
        result = await userinfo_class.get_user_info_jwt()
        return result

    except ClaimsNotFoundError:
        raise HTTPException(status_code=422, detail="Claims for user you are looking for does not exist")

    except:
        raise HTTPException(status_code=403, detail="Incorrect Token")


@userinfo_router.get('/get_default_token', response_model=str, tags=['UserInfo'])
async def get_default_token():
    try:
        uis = UserInfoServies()
        uis.jwt.set_expire_time(expire_hours= 1)
        return uis.jwt.encode_jwt(payload = {"sub":"1"})
    except:
        raise HTTPException(status_code=500)


@userinfo_router.get('/decode_token', response_model=dict, tags=['UserInfo'])
async def get_decode_token(token:str):
    try:
        uis = UserInfoServies()
        return uis.jwt.decode_token(token)
    except:
        raise HTTPException(status_code=500)
