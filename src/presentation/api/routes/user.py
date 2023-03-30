import logging
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from src.presentation.api.models.user import RequestUserModel  
from src.business_logic.services import AdminUserService
from src.di.providers.services import provide_admin_user_service_stub
from src.data_access.postgresql.errors import ClientNotFoundError
from src.dyna_config import DOMAIN_NAME
from fastapi.templating import Jinja2Templates

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
    ) -> None:

    kwargs = request_body.__dict__
    if await user_service.user_repo.validate_user_by_email(email=kwargs['email']):
        return templates.TemplateResponse("user_registration_failed_email.html", {'request': request})
    if await user_service.user_repo.validate_user_by_username(username=kwargs['username']):
        return templates.TemplateResponse("user_registration_failed_username.html", {'request': request})
    await user_service.registration(kwargs)
    return templates.TemplateResponse("user_registration_success.html", {'request': request})
    

@user_router.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("user_registration.html", {'request': request})

# @user_router.put("/{email}", response_class=dict, status_code=200)
# async def update_client(
#     client_id: str, 
#     request_body: RequestUserModel = Depends(),
#     user_service: AdminUserService = Depends(provide_admin_user_service)
#     ) -> None:
#     user_service.request_model = request_body
#     await user_service.update(client_id=client_id)
#     return {"message": "User data updated successfully"}


# @user_router.delete("/{email}", response_class=dict, status_code=status.HTTP_200_OK)
# async def delete_client(
#     email:str,
#     user_service: AdminUserService = Depends(provide_admin_user_service)
#     )->None:
#     await user_service.validate_password(email)
#     await user_service.delete_user(email)
#     return {"message": "User data updated successfully"}