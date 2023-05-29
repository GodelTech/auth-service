import logging
from functools import wraps
from typing import Union, TypeVar

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories import UserRepository
from src.business_logic.services.admin_api import AdminUserService
from src.data_access.postgresql.errors.user import DuplicationError
from src.presentation.admin_api.models.user import *
from src.di.providers import provide_async_session_stub
from typing import Callable
logger = logging.getLogger(__name__)

admin_user_router = APIRouter(prefix="/users")


@admin_user_router.get(
    "/{user_id}", response_model=dict, tags=["Administration User"]
)
async def get_user(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> dict[str, Any]:

    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )

    result = await user_class.get_user(user_id=user_id)
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
    "", status_code=status.HTTP_200_OK, tags=["Administration User"]
)
async def get_all_users(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestAllUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
    
) -> dict[str, Any]:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )
    return {
        "all_users": await user_class.get_all_users(
            group_id=request_model.group_id, role_id=request_model.role_id
        )
    }


@admin_user_router.put(
    "/{user_id}", status_code=200, tags=["Administration User"], description="update_user"
)
async def update_user(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    request_model: RequestUpdateUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )
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
        user_id=user_id, kwargs=data_to_change
    )
    await session.commit()

@admin_user_router.delete(
    "/{user_id}", status_code=200, tags=["Administration User"], description= "Delete User by ID"
)
async def delete_user(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )
    await user_class.delete_user(user_id=user_id)
    await session.commit()


@admin_user_router.post(
    "", status_code=200, tags=["Administration User"], description="Create a New User"
)
async def create_user(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_body: RequestCreateUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )
    data = request_body.dictionary()
    data["access_failed_count"] = 0

    await user_class.create_user(kwargs=data)
    await session.commit()


@admin_user_router.post(
    "/{user_id}/groups", status_code=200, tags=["Administration User"], description= "Add New Groups to the User"
)
async def add_groups(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    request_body: RequestGroupsUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )

    await user_class.add_user_groups(
        user_id=user_id, group_ids=request_body.group_ids
    )
    await session.commit()


@admin_user_router.post(
    "/{user_id}/roles", status_code=200, tags=["Administration User"]
)
async def add_roles(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    request_model: RequestRolesUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )
    await user_class.add_user_roles(
        user_id=user_id, role_ids=request_model.role_ids
    )
    await session.commit()
    return


@admin_user_router.get(
    "/{user_id}/groups", status_code=200, tags=["Administration User"]
)
async def get_user_groups(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    request_model: RequestUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
)  -> dict[str, Any]:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )

    return {
        "groups": await user_class.get_user_groups(
            user_id=user_id
        )
    }


@admin_user_router.get(
    "/{user_id}/roles", status_code=200, tags=["Administration User"], description= "Get Roles of User"
)
async def get_user_roles(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    request_model: RequestUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> dict[str, Any]:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )

    return {
        "roles": await user_class.get_user_roles(user_id=user_id)
    }


@admin_user_router.delete(
    "/{user_id}/roles", status_code=200, tags=["Administration User"], description="Delete Roles of the User"
)
async def delete_roles(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    request_model: RequestRolesUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )

    await user_class.remove_user_roles(
        user_id=user_id, role_ids=request_model.role_ids
    )
    await session.commit()


@admin_user_router.delete(
    "/{user_id}/groups", status_code=200, tags=["Administration User"], description="Delete Groups of the User"
)
async def delete_groups(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    request_model: RequestGroupsUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )

    await user_class.remove_user_groups(
        user_id=user_id, group_ids=request_model.group_ids
    )
    await session.commit()


@admin_user_router.put(
    "/{user_id}/password", status_code=200, tags=["Administration User"], description="Change User Password"
)
async def change_user_password(
    request: Request,
    user_id: int,
    access_token: str = Header(description="Access token"),
    request_model: RequestPasswordUserModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    session = session
    user_class = AdminUserService(
        session = session,
        user_repo=UserRepository(session)
        )

    await user_class.change_password(
        user_id=user_id, new_password=request_model.new_password
    )
    await session.commit()
