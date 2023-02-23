import logging
from functools import wraps
from typing import Union

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from src.business_logic.services.admin_api import AdminUserService
from src.data_access.postgresql.errors.user import DuplicationError
from src.di.providers.services import provide_admin_user_service_stub
from src.presentation.admin_api.models.user import *

logger = logging.getLogger(__name__)

admin_user_router = APIRouter(prefix="/user")


def exceptions_wrapper(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
            )
        except DuplicationError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Duplication"
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL_SERVER_ERROR",
            )

    return inner


@admin_user_router.get(
    "/get_user", response_model=dict, tags=["Administration User"]
)
@exceptions_wrapper
async def get_user(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):

    user_class = user_class

    result = await user_class.get_user(user_id=request_model.user_id)
    return {
        "username": result.username,
        "id": result.id,
        "phone_number": result.phone_number,
        "phone_number_confirmed": result.phone_number_confirmed,
        "email": result.email,
        "email_confirmed": result.email_confirmed,
        # "password_hash": result.password_hash,
        "lockout": result.lockout_enabled,
        "lockout_end_date_utc": result.lockout_end_date_utc,
    }


@admin_user_router.get(
    "/all_users", status_code=status.HTTP_200_OK, tags=["Administration User"]
)
@exceptions_wrapper
async def get_all_users(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestAllUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):

    user_class = user_class
    return {
        "all_users": await user_class.get_all_users(
            group_id=request_model.group_id, role_id=request_model.role_id
        )
    }


@admin_user_router.put(
    "/update_user", status_code=200, tags=["Administration User"]
)
@exceptions_wrapper
async def update_user(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestUpdateUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):
    user_class = user_class
    data_to_change = {}
    for param in (
        "username",
        "email",
        "email_confirmed",
        "phone_number",
        "phone_number_confirmed",
        "two_factors_enabled",
        "lockout_end_date_utc",
        "lockout_enabled",
    ):
        if getattr(request_model, param, False):
            data_to_change[param] = getattr(request_model, param)

    await user_class.update_user(
        user_id=request_model.user_id, kwargs=data_to_change
    )


@admin_user_router.delete(
    "/delete_user", status_code=200, tags=["Administration User"]
)
@exceptions_wrapper
async def delete_user(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):

    user_class = user_class
    await user_class.delete_user(user_id=request_model.user_id)


@admin_user_router.post(
    "/new_user", status_code=200, tags=["Administration User"]
)
# @exceptions_wrapper
async def create_user(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_body: RequestCreateUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):

    user_class = user_class
    data = request_body.dictionary()
    data["access_failed_count"] = 0

    await user_class.create_user(kwargs=data)


@admin_user_router.post(
    "/add_groups", status_code=200, tags=["Administration User"]
)
@exceptions_wrapper
async def add_groups(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_body: RequestGroupsUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):

    user_class = user_class

    await user_class.add_user_groups(
        user_id=request_body.user_id, group_ids=request_body.group_ids
    )


@admin_user_router.post(
    "/add_roles", status_code=200, tags=["Administration User"]
)
@exceptions_wrapper
async def add_roles(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestRolesUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):

    user_class = user_class
    await user_class.add_user_roles(
        user_id=request_model.user_id, role_ids=request_model.role_ids
    )
    return


@admin_user_router.get(
    "/show_groups", status_code=200, tags=["Administration User"]
)
@exceptions_wrapper
async def get_user_groups(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):

    user_class = user_class

    return {
        "groups": await user_class.get_user_groups(
            user_id=request_model.user_id
        )
    }


@admin_user_router.get(
    "/show_roles", status_code=200, tags=["Administration User"]
)
@exceptions_wrapper
async def get_user_roles(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):
    user_class = user_class

    return {
        "roles": await user_class.get_user_roles(user_id=request_model.user_id)
    }


@admin_user_router.delete(
    "/delete_user_roles", status_code=200, tags=["Administration User"]
)
@exceptions_wrapper
async def delete_roles(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestRolesUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):
    user_class = user_class

    await user_class.remove_user_roles(
        user_id=request_model.user_id, role_ids=request_model.role_ids
    )


@admin_user_router.delete(
    "/delete_user_groups", status_code=200, tags=["Administration User"]
)
@exceptions_wrapper
async def delete_groups(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestGroupsUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):

    user_class = user_class

    await user_class.remove_user_groups(
        user_id=request_model.user_id, group_ids=request_model.group_ids
    )


@admin_user_router.put(
    "/change_user_password", status_code=200, tags=["Administration User"]
)
@exceptions_wrapper
async def change_user_password(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestPasswordUserModel = Depends(),
    user_class: AdminUserService = Depends(provide_admin_user_service_stub),
):

    user_class = user_class

    await user_class.change_password(
        user_id=request_model.user_id, new_password=request_model.new_password
    )
