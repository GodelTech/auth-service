import mock

mock.patch(
    "fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f
).start()

from typing import AsyncIterator, Any

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import get_application

from src.business_logic.services.authorization import AuthorizationService
from src.business_logic.services.endsession import EndSessionService
from src.business_logic.services.userinfo import UserInfoServices
from src.data_access.postgresql.repositories import (
    ClientRepository,
    UserRepository,
    PersistentGrantRepository,
)
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.introspection import IntrospectionServies
from src.business_logic.services.tokens import TokenService

from src.di import Container

from pytest_postgresql import factories
import os


TEST_SQL_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_sql"

# Using the factory to create a postgresql instance
postgresql_proc = factories.postgresql_proc()

postgresql_load = factories.postgresql(
    "postgresql_proc",
    dbname="test-load-db",
    load=[
        TEST_SQL_DIR + "/table_clients.sql",
        TEST_SQL_DIR + "/table_persistent_grants.sql",
        TEST_SQL_DIR + "/inserts.sql",
    ],
)


@pytest_asyncio.fixture
async def connection(postgresql_load: factories.postgresql) -> Any:
    return postgresql_load


@pytest_asyncio.fixture
async def app() -> FastAPI:
    return get_application()


# @pytest_asyncio.fixture
# async def connection(app: FastAPI) -> AsyncIterator[AsyncSession]:
#     async with app.container.db().session_factory() as conn:
#         yield conn


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest_asyncio.fixture
async def engine(app: FastAPI) -> Any:
    return app.container.db().engine


@pytest_asyncio.fixture
async def authorization_service() -> AuthorizationService:
    engine = Container.db().engine
    auth_service = AuthorizationService(
        client_repo=ClientRepository(engine),
        user_repo=UserRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        password_service=PasswordHash(),
    )
    return auth_service


@pytest_asyncio.fixture
async def end_session_service() -> EndSessionService:
    engine = Container.db().engine
    end_sess_service = EndSessionService(
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        jwt_service=JWTService(),
    )
    return end_sess_service


@pytest_asyncio.fixture
async def introspection_service() -> IntrospectionServies:
    engine = Container.db().engine
    intro_service = IntrospectionServies(
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        user_repo=UserRepository(engine),
        jwt=JWTService(),
    )
    return intro_service


@pytest_asyncio.fixture
async def user_info_service() -> UserInfoServices:
    engine = Container.db().engine
    user_info = UserInfoServices(
        jwt=JWTService(),
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        user_repo=UserRepository(engine),
    )
    return user_info


@pytest_asyncio.fixture
async def token_service() -> TokenService:
    engine = Container.db().engine
    tk_service = TokenService(
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        user_repo=UserRepository(engine),
        jwt_service=JWTService(),
    )
    return tk_service
