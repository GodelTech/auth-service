import mock
import os

mock.patch(
    "fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f
).start()
from fastapi import Request
from typing import AsyncIterator, Any

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import pytest
import asyncio
from src.main import get_application
from src.business_logic.services.authorization.authorization_service import (
    AuthorizationService,
)
from src.business_logic.services.endsession import EndSessionService
from src.business_logic.services.userinfo import UserInfoServices
from src.business_logic.services import DeviceService, WellKnownServices

from src.data_access.postgresql.repositories import (
    ClientRepository,
    UserRepository,
    PersistentGrantRepository,
    DeviceRepository,
    ThirdPartyOIDCRepository,
    WellKnownRepository,
    BlacklistedTokenRepository,
)
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.introspection import IntrospectionServies
from src.business_logic.services.tokens import TokenService
from src.business_logic.services.login_form_service import LoginFormService
from src.business_logic.services.third_party_oidc_service import (
    AuthThirdPartyOIDCService,
    ThirdPartyGoogleService,
    ThirdPartyMicrosoftService,
    ThirdPartyGitLabService,
)
from src.data_access.postgresql.tables.base import Base


from tests.overrides.override_test_container import CustomPostgresContainer
from factories.commands import DataBasePopulation
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import scoped_session, sessionmaker


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncEngine:
    postgres_container = CustomPostgresContainer(
        "postgres:11.5"
    ).with_bind_ports(5432, 5465)

    with postgres_container as postgres:
        db_url = postgres.get_connection_url()
        db_url = db_url.replace("psycopg2", "asyncpg")
        engine = create_async_engine(db_url, echo=True)

        # create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # populate database
        DataBasePopulation.populate_database()

        yield engine


@pytest_asyncio.fixture(scope="function")
async def connection(engine: AsyncEngine) -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def app() -> FastAPI:
    return get_application()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop(request: Request) -> Any:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def authorization_service(connection: AsyncSession) -> AuthorizationService:
    auth_service = AuthorizationService(
        session=connection,
        client_repo=ClientRepository(session=connection),
        user_repo=UserRepository(session=connection),
        persistent_grant_repo=PersistentGrantRepository(session=connection),
        device_repo=DeviceRepository(session=connection),
        password_service=PasswordHash(),
        jwt_service=JWTService(),
    )
    return auth_service


@pytest_asyncio.fixture
async def end_session_service(connection: AsyncSession) -> EndSessionService:
    end_sess_service = EndSessionService(
        session=connection,
        client_repo=ClientRepository(session=connection),
        persistent_grant_repo=PersistentGrantRepository(session=connection),
        jwt_service=JWTService(),
    )
    return end_sess_service


@pytest_asyncio.fixture
async def introspection_service(connection: AsyncSession) -> IntrospectionServies:
    intro_service = IntrospectionServies(
        session=connection,
        client_repo=ClientRepository(session=connection),
        persistent_grant_repo=PersistentGrantRepository(session=connection),
        user_repo=UserRepository(session=connection),
        jwt=JWTService(),
    )
    return intro_service


@pytest_asyncio.fixture
async def user_info_service(connection: AsyncSession) -> UserInfoServices:
    user_info = UserInfoServices(
        session=connection,
        jwt=JWTService(),
        client_repo=ClientRepository(session=connection),
        persistent_grant_repo=PersistentGrantRepository(session=connection),
        user_repo=UserRepository(session=connection),
    )
    return user_info


@pytest_asyncio.fixture
async def token_service(connection: AsyncSession) -> TokenService:
    tk_service = TokenService(
        session=connection,
        client_repo=ClientRepository(session=connection),
        persistent_grant_repo=PersistentGrantRepository(session=connection),
        user_repo=UserRepository(session=connection),
        device_repo=DeviceRepository(session=connection),
        jwt_service=JWTService(),
        blacklisted_repo=BlacklistedTokenRepository(session=connection),
    )
    return tk_service


@pytest_asyncio.fixture
async def login_form_service(connection: AsyncSession) -> LoginFormService:
    login_service = LoginFormService(
        session=connection,
        client_repo=ClientRepository(session=connection),
        oidc_repo=ThirdPartyOIDCRepository(session=connection),
    )
    return login_service


@pytest_asyncio.fixture
async def device_service(connection: AsyncSession) -> DeviceService:
    dev_service = DeviceService(
        session=connection,
        client_repo=ClientRepository(session=connection),
        device_repo=DeviceRepository(session=connection),
    )
    return dev_service


@pytest_asyncio.fixture
async def auth_third_party_service(connection: AsyncSession) -> AuthThirdPartyOIDCService:
    third_party_service = AuthThirdPartyOIDCService(
        session=connection,
        client_repo=ClientRepository(connection),
        user_repo=UserRepository(connection),
        persistent_grant_repo=PersistentGrantRepository(connection),
        oidc_repo=ThirdPartyOIDCRepository(connection),
        http_client=AsyncClient(),
    )
    return third_party_service


@pytest_asyncio.fixture
async def google_third_party_service(connection) -> ThirdPartyGoogleService:
    google_service = ThirdPartyGoogleService(
        session=connection,
        client_repo=ClientRepository(connection),
        user_repo=UserRepository(connection),
        persistent_grant_repo=PersistentGrantRepository(connection),
        oidc_repo=ThirdPartyOIDCRepository(connection),
        http_client=AsyncClient(),
    )
    return google_service


@pytest_asyncio.fixture
async def gitlab_third_party_service(connection) -> ThirdPartyGitLabService:
    gitlab_service = ThirdPartyGitLabService(
        session=connection,
        client_repo=ClientRepository(connection),
        user_repo=UserRepository(connection),
        persistent_grant_repo=PersistentGrantRepository(connection),
        oidc_repo=ThirdPartyOIDCRepository(connection),
        http_client=AsyncClient(),
    )
    return gitlab_service


@pytest_asyncio.fixture
async def microsoft_third_party_service(connection) -> ThirdPartyMicrosoftService:
    microsoft_service = ThirdPartyMicrosoftService(
        client_repo=ClientRepository(connection),
        session=connection,
        user_repo=UserRepository(connection),
        persistent_grant_repo=PersistentGrantRepository(connection),
        oidc_repo=ThirdPartyOIDCRepository(connection),
        http_client=AsyncClient(),
    )
    return microsoft_service


@pytest_asyncio.fixture
async def wlk_services(connection: AsyncSession) -> WellKnownServices:
    wlk_services = WellKnownServices(
        session=connection,
        wlk_repo=WellKnownRepository(session=connection),
    )
    return wlk_services


from src.business_logic.services.admin_auth import AdminAuthService


@pytest_asyncio.fixture
async def admin_auth_service(connection: AsyncSession) -> AdminAuthService:
    admin_auth_service = AdminAuthService(
        user_repo=UserRepository(session=connection),
        password_service=PasswordHash(),
        jwt_service=JWTService(),
    )
    return admin_auth_service
