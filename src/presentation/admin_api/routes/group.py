import logging
from functools import wraps

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from typing import Callable, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.repositories import GroupRepository
from src.business_logic.services.admin_api import AdminGroupService
# from src.data_access.postgresql.errors.user import DuplicationError
from src.presentation.admin_api.models.group import *
from src.di.providers import provide_async_session_stub

logger = logging.getLogger(__name__)

admin_group_router = APIRouter(prefix="/groups")


@admin_group_router.get(
    "/{group_id}", response_model=dict, tags=["Administration Group"], description="Get the Group"
)
async def get_group(
    request: Request,
    group_id:int,
    access_token: str = Header(description="Access token"),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> dict[str, Any]:
    group_class = AdminGroupService(
        session=session,
        group_repo=GroupRepository(session=session)
    )

    result = await group_class.get_group(group_id=group_id)
    return {
        "id": result.id,
        "name": result.name,
        "parent_group": result.parent_group,
    }


@admin_group_router.get(
    "", response_model=dict, tags=["Administration Group"], description="Get All Groups"
)
async def get_all_groups(
    request: Request,
    access_token: str = Header(description="Access token"),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> dict[str, Any]:
    group_class = AdminGroupService(
        session=session,
        group_repo=GroupRepository(session=session)
    )
    
    return {"all_groups": await group_class.get_all_groups()}


@admin_group_router.get(
    "/{group_id}/subgroups", response_model=dict, tags=["Administration Group"], description="Get Subgroups of the Group"
)
async def get_subgroups(
    request: Request,
    group_id:int,
    access_token: str = Header(description="Access token"),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> dict[str, Any]:
    group_class = AdminGroupService(
        session=session,
        group_repo=GroupRepository(session=session)
    )
    
    result = await group_class.get_subgroups(group_id=group_id)
    return result


@admin_group_router.post(
    "", status_code=status.HTTP_200_OK, tags=["Administration Group"], description="Create a New Group"
)
async def create_group(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestNewGroupModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    group_class = AdminGroupService(
        session=session,
        group_repo=GroupRepository(session=session)
    )
    
    await group_class.create_group(
        name=request_model.name, parent_group=request_model.parent_group
    )
    await session.commit()


@admin_group_router.put(
    "/{group_id}",
    status_code=status.HTTP_200_OK,
    tags=["Administration Group"],
    description="Update the Group"
)
async def update_group(
    request: Request,
    group_id:int,
    access_token: str = Header(description="Access token"),
    request_model: RequestUpdateGroupModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    group_class = AdminGroupService(
        session=session,
        group_repo=GroupRepository(session=session)
    )
    
    await group_class.update_group(
        group_id=group_id,
        name=request_model.name,
        parent_group=request_model.parent_group,
    )
    await session.commit()


@admin_group_router.delete(
    "/{group_id}",
    status_code=status.HTTP_200_OK,
    tags=["Administration Group"],
    description="Delete the Group"
)
async def delete_group(
    request: Request,
    group_id:int,
    access_token: str = Header(description="Access token"),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    group_class = AdminGroupService(
        session=session,
        group_repo=GroupRepository(session=session)
    )
    await group_class.delete_group(group_id=group_id)
    await session.commit()
