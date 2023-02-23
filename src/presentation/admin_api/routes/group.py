import logging
from functools import wraps

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from src.business_logic.services.admin_api import AdminGroupService
from src.data_access.postgresql.errors.user import DuplicationError
from src.di.providers.services import provide_admin_group_service_stub
from src.presentation.admin_api.models.group import *

logger = logging.getLogger(__name__)

admin_group_router = APIRouter(prefix="/group")


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


@admin_group_router.get(
    "/get_group", response_model=dict, tags=["Administration Group"]
)
@exceptions_wrapper
async def get_group(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestDefaultGroupModel = Depends(),
    group_class: AdminGroupService = Depends(provide_admin_group_service_stub),
):

    group_class = group_class

    result = await group_class.get_group(group_id=request_model.group_id)
    return {
        "id": result.id,
        "name": result.name,
        "parent_group": result.parent_group,
    }


@admin_group_router.get(
    "/get_all_groups", response_model=dict, tags=["Administration Group"]
)
@exceptions_wrapper
async def get_all_groups(
    request: Request,
    access_token: str = Header(description="Access token"),
    group_class: AdminGroupService = Depends(provide_admin_group_service_stub),
):
    group_class = group_class
    return {"all_groups": await group_class.get_all_groups()}


@admin_group_router.get(
    "/get_subgroups", response_model=dict, tags=["Administration Group"]
)
@exceptions_wrapper
async def get_subgroups(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestDefaultGroupModel = Depends(),
    group_class: AdminGroupService = Depends(provide_admin_group_service_stub),
):
    group_class = group_class
    result = await group_class.get_subgroups(group_id=request_model.group_id)
    return result


@admin_group_router.post(
    "/new_group", status_code=status.HTTP_200_OK, tags=["Administration Group"]
)
@exceptions_wrapper
async def create_group(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestNewGroupModel = Depends(),
    group_class: AdminGroupService = Depends(provide_admin_group_service_stub),
):
    group_class = group_class
    await group_class.create_group(
        name=request_model.name, parent_group=request_model.parent_group
    )


@admin_group_router.put(
    "/update_group",
    status_code=status.HTTP_200_OK,
    tags=["Administration Group"],
)
@exceptions_wrapper
async def update_group(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestUpdateGroupModel = Depends(),
    group_class: AdminGroupService = Depends(provide_admin_group_service_stub),
):
    group_class = group_class
    await group_class.update_group(
        group_id=request_model.group_id,
        name=request_model.name,
        parent_group=request_model.parent_group,
    )


@admin_group_router.delete(
    "/delete_group",
    status_code=status.HTTP_200_OK,
    tags=["Administration Group"],
)
@exceptions_wrapper
async def delete_group(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestGroupModel = Depends(),
    group_class: AdminGroupService = Depends(provide_admin_group_service_stub),
):
    group_class = group_class
    await group_class.delete_group(group_id=request_model.group_id)
