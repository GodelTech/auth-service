import mock
import os

mock.patch(
    "fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f
).start()

from typing import AsyncIterator

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import pytest
import asyncio
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
from src.business_logic.services.login_form_service import LoginFormService
from src.data_access.postgresql.tables.base import Base

from src.di.providers import (
    provide_auth_service_stub,
    provide_endsession_service_stub,
    provide_introspection_service_stub,
    provide_token_service_stub,
    provide_userinfo_service_stub,
    provide_login_form_service_stub,
)

from tests.overrides.override_functions import (
    nodepends_provide_auth_service_override,
    nodepends_provide_endsession_servise_override,
    nodepends_provide_introspection_service_override,
    nodepends_provide_token_service_override,
    nodepends_provide_userinfo_service_override,
    nodepends_provide_login_form_service_override,
)
from tests.overrides.override_test_container import CustomPostgresContainer
from sqlalchemy import text


TEST_SQL_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_sql"


@pytest_asyncio.fixture(scope="session")
async def engine():
    postgres_container = CustomPostgresContainer("postgres:9.5").with_bind_ports(
        5432, 5463
    )
    with postgres_container as postgres:
        db_url = postgres.get_connection_url()
        db_url = db_url.replace("psycopg2", "asyncpg")
        engine = create_async_engine(db_url, echo=True)
        async with engine.begin() as conn:
            # create all tables
            await conn.run_sync(Base.metadata.create_all)

            # create queries of insert statements from sql files
            users = open(TEST_SQL_DIR + "/users.sql")
            query_users = text(users.read())
            user_claims = open(TEST_SQL_DIR + "/user_claims.sql")
            query_user_claims = text(user_claims.read())
            clients = open(TEST_SQL_DIR + "/clients.sql")
            query_clients = text(clients.read())
            client_secrets = open(TEST_SQL_DIR + "/client_secrets.sql")
            query_client_secrets = text(client_secrets.read())
            client_redirect_uris = open(
                TEST_SQL_DIR + "/client_redirect_uris.sql"
            )
            query_client_redirect_uris = text(client_redirect_uris.read())
            client_post_logout_redirect_uris = open(
                TEST_SQL_DIR + "/client_post_logout_redirect_uris.sql"
            )
            query_client_post_logout_redirect_uris = text(
                client_post_logout_redirect_uris.read()
            )

            # populate database by executing queries
            await conn.execute(query_clients)
            await conn.execute(query_users)
            await conn.execute(query_user_claims)
            await conn.execute(query_client_post_logout_redirect_uris)
            await conn.execute(query_client_secrets)
            await conn.execute(query_client_redirect_uris)

        yield engine


@pytest_asyncio.fixture(scope="session")
async def connection(engine):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def app() -> FastAPI:
    app = get_application()

    # override stubs to use test db_uri
    app.dependency_overrides[
        provide_auth_service_stub
    ] = nodepends_provide_auth_service_override
    app.dependency_overrides[
        provide_endsession_service_stub
    ] = nodepends_provide_endsession_servise_override
    app.dependency_overrides[
        provide_introspection_service_stub
    ] = nodepends_provide_introspection_service_override
    app.dependency_overrides[
        provide_token_service_stub
    ] = nodepends_provide_token_service_override
    app.dependency_overrides[
        provide_userinfo_service_stub
    ] = nodepends_provide_userinfo_service_override
    app.dependency_overrides[
        provide_login_form_service_stub
    ] = nodepends_provide_login_form_service_override

    return app


@pytest_asyncio.fixture
async def client(app: FastAPI, connection) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def authorization_service(engine) -> AuthorizationService:
    auth_service = AuthorizationService(
        client_repo=ClientRepository(engine),
        user_repo=UserRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        password_service=PasswordHash(),
    )
    return auth_service


@pytest_asyncio.fixture
async def end_session_service(engine) -> EndSessionService:
    end_sess_service = EndSessionService(
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        jwt_service=JWTService(),
    )
    return end_sess_service


@pytest_asyncio.fixture
async def introspection_service(engine) -> IntrospectionServies:
    intro_service = IntrospectionServies(
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        user_repo=UserRepository(engine),
        jwt=JWTService(),
    )
    return intro_service


@pytest_asyncio.fixture
async def user_info_service(engine) -> UserInfoServices:
    user_info = UserInfoServices(
        jwt=JWTService(),
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        user_repo=UserRepository(engine),
    )
    return user_info


@pytest_asyncio.fixture
async def token_service(engine) -> TokenService:
    tk_service = TokenService(
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        user_repo=UserRepository(engine),
        jwt_service=JWTService(),
    )
    return tk_service


@pytest_asyncio.fixture
async def login_form_service(engine) -> LoginFormService:
    login_service = LoginFormService(
        client_repo=ClientRepository(engine),
    )
    return login_service
