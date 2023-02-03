import logging
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from src.di.providers.services import provide_admin_role_service_stub
from functools import wraps
from src.business_logic.services.admin_api import AdminRoleService
from src.presentation.admin_api.models.role import *
from src.data_access.postgresql.errors.user import DuplicationError


logger = logging.getLogger("is_app")

admin_role_router = APIRouter(prefix="/role")

def exceptions_wrapper(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Not found"
        )
        except DuplicationError:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Duplication"
        )
        except:
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="INTERNAL_SERVER_ERROR"
        )
    return inner


@admin_role_router.get(
    "/get_role", response_model=dict, tags=["Administration Role"]
)
@exceptions_wrapper
async def get_role(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestRoleModel = Depends(),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):

    role_class = role_class

    result = await role_class.get_role(role_id=request_model.role_id)
    return {"role" : result}


@admin_role_router.get(
    "/get_all_roles", response_model=dict, tags=["Administration Role"]
)
@exceptions_wrapper
async def get_all_roles(
    request: Request,
    access_token: str = Header(description="Access token"),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):
    role_class = role_class
    return { "all_roles" : await role_class.get_all_roles()}


@admin_role_router.post(
    "/get_roles", response_model=dict, tags=["Administration Role"]
)
@exceptions_wrapper
async def get_all_roles(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestListRoleModel = Depends(),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):
    role_class = role_class
    return { "list_roles" : await role_class.get_roles(role_ids=request_model.role_ids)}


@admin_role_router.post(
    "/new_role", status_code=status.HTTP_200_OK, tags=["Administration Role"]
)
@exceptions_wrapper
async def create_role(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestNewRoleModel = Depends(),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):
    role_class = role_class
    await role_class.create_role(name=request_model.name)


@admin_role_router.put(
    "/update_role", status_code=status.HTTP_200_OK, tags=["Administration Role"]
)
@exceptions_wrapper
async def update_role(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestUpdateRoleModel = Depends(),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):
    role_class = role_class
    await role_class.update_role(role_id=request_model.role_id, name=request_model.name)


@admin_role_router.delete(
    "/delete_role", status_code=status.HTTP_200_OK, tags=["Administration Role"]
)
@exceptions_wrapper
async def delete_group(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestRoleModel = Depends(),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):
    role_class = role_class
    await role_class.delete_role(role_id=request_model.role_id)
    