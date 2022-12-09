from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy_utils import ChoiceType
from src.business_logic.services.userinfo import UserInfoServies
from src.presentation.api.models.userinfo import ResponseUserInfoModel, RequestUserInfoModel


userinfo_router = APIRouter(
    prefix='/userinfo',
)


@userinfo_router.get('/', response_model=ResponseUserInfoModel,)
async def get_userinfo(request: RequestUserInfoModel = Depends(), userinfo_class: UserInfoServies = Depends()):
    try:
        userinfo_class = userinfo_class
        userinfo_class.request = request
        return await userinfo_class.get_user_info()
    except:
        raise HTTPException(status_code=403, detail="Incorrect Token")


@userinfo_router.get('/jwt', response_model=str,)
async def get_userinfo_jwt(request: RequestUserInfoModel = Depends(), userinfo_class: UserInfoServies = Depends()):
    try:
        userinfo_class = userinfo_class
        userinfo_class.request = request
        result = await userinfo_class.get_user_info_jwt()
        return result
    except:
        raise HTTPException(status_code=403, detail="Incorrect Token")

@userinfo_router.get('/get_default_token', response_model=str,)
async def get_default_token():
    try:
        uis = UserInfoServies()
        return uis.jwt.encode_jwt()
    except:
        raise HTTPException(status_code=500)