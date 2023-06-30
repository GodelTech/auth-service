import logging
from functools import wraps

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from typing import Callable, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.repositories import RoleRepository
from src.business_logic.services.admin_api import AdminRoleService
from src.data_access.postgresql.errors.user import DuplicationError
from src.presentation.admin_api.models.role import *
from src.di.providers import provide_async_session_stub

logger = logging.getLogger(__name__)

admin_role_router = APIRouter(prefix="/roles")


@admin_role_router.get(
    "/{role_id}", response_model=dict, tags=["Administration Role"], description="Get the Role"
)
async def get_role(
    request: Request,
    role_id:int,
    access_token: str = Header(description="Access token"),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> dict[str, Any]:
        role_class = AdminRoleService(
            session=session,
            role_repo=RoleRepository(session)
        )
        result = await role_class.get_role(role_id=role_id)
        return {"role": result}


@admin_role_router.get(
    "", response_model=dict, tags=["Administration Role"], description="Get All Roles"
)
async def get_all_roles(
    request: Request,
    access_token: str = Header(description="Access token"),
    session: AsyncSession = Depends(provide_async_session_stub)
)-> dict[str, Any]:
    role_class = AdminRoleService(
            session=session,
            role_repo=RoleRepository(session)
        )
    return {"all_roles": await role_class.get_all_roles()}


@admin_role_router.post(
    "", status_code=status.HTTP_200_OK, tags=["Administration Role"], description="Create a New Role"
)
async def create_role(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestNewRoleModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    role_class = AdminRoleService(
            session=session,
            role_repo=RoleRepository(session)
        )
    await role_class.create_role(name=request_model.name)
    await session.commit()


@admin_role_router.put(
    "/{role_id}", status_code=status.HTTP_200_OK, tags=["Administration Role"], description="Update the Role"
)
async def update_role(
    request: Request,
    role_id:int,
    access_token: str = Header(description="Access token"),
    request_model: RequestUpdateRoleModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
        role_class = AdminRoleService(
            session=session,
            role_repo=RoleRepository(session)
        )
        await role_class.update_role(
            role_id=role_id, name=request_model.name
        )
        await session.commit()

@admin_role_router.delete(
    "/{role_id}", status_code=status.HTTP_200_OK, tags=["Administration Role"], description="Delete the Role"
)
async def delete_group(
    request: Request,
    role_id:int,
    access_token: str = Header(description="Access token"),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    role_class = AdminRoleService(
        session=session,
        role_repo=RoleRepository(session=session)
    )
    await role_class.delete_role(role_id=role_id)
    await session.commit()
