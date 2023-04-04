import logging
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from src.presentation.api.models.user import RequestUserModel, RequestLoginModel
from src.business_logic.services import AdminUserService
from src.di.providers.services import provide_admin_user_service_stub
from src.data_access.postgresql.errors import ClientNotFoundError
from src.dyna_config import DOMAIN_NAME
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from pydantic import SecretStr
from src.business_logic.services.jwt_token import JWTService
from time import time
from typing import Union

logger = logging.getLogger(__name__)

user_router = APIRouter(
    prefix="/user", tags=["User"]
)

templates = Jinja2Templates(directory="src/presentation/api/templates/")

@user_router.post("/register", status_code=200)
async def register_user(
    request: Request,
    request_body: RequestUserModel = Depends(),
    user_service: AdminUserService = Depends(provide_admin_user_service_stub)
    ) -> _TemplateResponse:

    kwargs = request_body.__dict__
    if await user_service.user_repo.validate_user_by_email(email=kwargs['email']):
        return templates.TemplateResponse("user_registration_failed_email.html", {'request': request})
    if await user_service.user_repo.validate_user_by_username(username=kwargs['username']):
        return templates.TemplateResponse("user_registration_failed_username.html", {'request': request})
    await user_service.registration(kwargs)
    return templates.TemplateResponse("user.html", {'request': request})
    

@user_router.get("/register", response_class=HTMLResponse)
def register(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("user_registration.html", {'request': request})

@user_router.get("/login", response_class=HTMLResponse)
def login(request: Request) -> _TemplateResponse:
    template =  templates.TemplateResponse("login.html", {'request': request})
    return template

@user_router.get("/{email}", response_class=HTMLResponse)
async def get_user(
    email: str,
    request: Request,
    auth_swagger: Union[str, None] = Header(
    default=None, description="Authorization"
    ),  # crutch for swagger
    user_service: AdminUserService = Depends(provide_admin_user_service_stub)
    )  -> _TemplateResponse:
    token =auth_swagger or request.headers.get('Authorization')
    email_from_token = (await JWTService().decode_token(token=token,  audience='user'))['sub']
    if email_from_token == email:
        user = await user_service.user_repo.get_user_by_email(email=email)
        user_data = user_service.user_to_dict(user=user)

        return templates.TemplateResponse("user.html", {'request': request, 'user':user_data})
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Auth Token")


@user_router.post("/login", response_class=JSONResponse, status_code=status.HTTP_200_OK)
async def get_client(
    request: Request,
    request_body: RequestLoginModel = Depends(),
    user_service: AdminUserService = Depends(provide_admin_user_service_stub)
    )-> _TemplateResponse:
    
    try:
        flag, user = await user_service.validate_password(email=request_body.email, password=request_body.password)
    except:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    user_data = user_service.user_to_dict(user=user)
    #TODO: rework after new logic 
    access_token = await JWTService().encode_jwt({'sub':request_body.email,'aud':'user', 'exp': time()+15*60})
    return JSONResponse({"access_token":access_token, "token_type": "Bearer"})
    
@user_router.get("", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_redirection(
    request: Request
    ):
    return templates.TemplateResponse("redirection_user.html", {'request': request})
    