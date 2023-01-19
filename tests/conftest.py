import mock
mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

from typing import AsyncIterator

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import get_application

from src.business_logic.services.authorization import AuthorizationService
from src.business_logic.services.endsession import EndSessionService
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.userinfo import UserInfoServices
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.tokens import TokenService

from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository,
)


@pytest_asyncio.fixture
async def app() -> FastAPI:
    return get_application()


@pytest_asyncio.fixture
async def connection(app: FastAPI) -> AsyncIterator[AsyncSession]:
    async with app.container.db().session_factory() as conn:
        yield conn


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest_asyncio.fixture
async def authorization_service(
    connection: AsyncIterator[AsyncSession],
) -> AuthorizationService:
    auth_service = AuthorizationService(
        client_repo=ClientRepository(connection),
        user_repo=UserRepository(connection),
        persistent_grant_repo=PersistentGrantRepository(connection),
        password_service=PasswordHash(),
    )

    return auth_service


@pytest_asyncio.fixture
async def end_session_service(connection: AsyncSession) -> EndSessionService:
    end_sess_service = EndSessionService(
        client_repo=ClientRepository(connection),
        persistent_grant_repo=PersistentGrantRepository(connection)
    )

    return end_sess_service


@pytest_asyncio.fixture
async def user_info_service(connection: AsyncSession) -> UserInfoServices:
    user_info_service = UserInfoServices(
        user_repo=UserRepository(connection),
        client_repo=ClientRepository(connection),
        persistent_grant_repo=PersistentGrantRepository(connection),
        token_service=TokenService()
    )

    return user_info_service
