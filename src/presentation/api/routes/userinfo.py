from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import Optional
from src.business_logic.services.userinfo import UserInfoServies
from src.presentation.api.models.userinfo import ResponseUserInfoModel, RequestUserInfoModel
from fastapi_cache.decorator import cache
from fastapi_cache.coder import JsonCoder 
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from src.config.settings.cache_time import CacheTimeSettings
from src.business_logic.cache.key_builders import builder_with_parametr
import logging, time
import json

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
    except:
        raise HTTPException(status_code=403, detail="Incorrect Token")

@userinfo_router.get('/get_default_token', response_model=str, tags=['UserInfo'])
async def get_default_token():
    try:
        uis = UserInfoServies()
        return uis.jwt.encode_jwt()
    except:
        raise HTTPException(status_code=500)