import mock
from sqlalchemy import delete, insert

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
from src.business_logic.services import (
    DeviceService,
    WellKnownServices,
    ClientService,
)

from src.data_access.postgresql.repositories import (
    ClientRepository,
    UserRepository,
    PersistentGrantRepository,
    DeviceRepository,
    ThirdPartyOIDCRepository,
    WellKnownRepository,
    BlacklistedTokenRepository,
    CodeChallengeRepository,
)
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.introspection import IntrospectionService
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
from sqlalchemy.orm import sessionmaker
from src.data_access.postgresql.tables import (
    IdentityClaim,
    IdentityResource,
    IdentityProviderMapped,
    Device,
    ClientSecret,
    ClientRedirectUri,
    ClientCorsOrigin,
    ClientPostLogoutRedirectUri,
    ClientClaim,
    ClientScope,
    ClientIdRestriction,
    Client,
    RefreshTokenUsageType,
    RefreshTokenExpirationType,
    ProtocolType,
    AccessTokenType,
    # ClientGrantType,
    UserClaim,
    UserClaimType,
    UserPassword,
    User,
    Role,
    Permission,
    Group,
    ApiScopeClaim,
    ApiScope,
    ApiClaim,
    ApiSecret,
    ApiScopeClaimType,
    ApiClaimType,
    ApiSecretType,
    ApiResource,
    PersistentGrant,
    PersistentGrantType,
)
import datetime


@pytest_asyncio.fixture(scope="session", autouse=True)
async def container() -> AsyncIterator[CustomPostgresContainer]:
    postgres_container = CustomPostgresContainer(
        "postgres:11.5"
    ).with_bind_ports(5432, 5465)

    with postgres_container as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="session", autouse=True)
async def engine(container: CustomPostgresContainer) -> AsyncEngine:
    db_url = container.get_connection_url()
    db_url = db_url.replace("psycopg2", "asyncpg")
    engine = create_async_engine(db_url, echo=False)

    # create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # populate database
    DataBasePopulation.clean_and_populate()

    yield engine


@pytest_asyncio.fixture(autouse=True)
async def pre_test_setup() -> None:
    DataBasePopulation.clean_and_populate()


@pytest_asyncio.fixture
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
async def authorization_service(
    connection: AsyncSession,
) -> AuthorizationService:
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
async def introspection_service(
    connection: AsyncSession,
) -> IntrospectionService:
    intro_service = IntrospectionService(
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
        code_challenge_repo=CodeChallengeRepository(session=connection),
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
        code_challenge_repo=CodeChallengeRepository(session=connection),
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
async def auth_third_party_service(
    connection: AsyncSession,
) -> AuthThirdPartyOIDCService:
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
async def microsoft_third_party_service(
    connection,
) -> ThirdPartyMicrosoftService:
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
async def wlk_services(connection: AsyncSession) -> WellKnownService:
    wlk_services = WellKnownService(
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


# @pytest_asyncio.fixture
# async def token():
#     jwt_service = JWTService()
#     token = await jwt_service.encode_jwt(
#             payload={
#                 "sub": 1,
#                 "exp": time.time() + 3600,
#                 "aud": ["admin", "introspection", "revoke"]
#             }
#         )
#     return token

# @pytest_asyncio.fixture
# async def admin_credentials():
#     return {
#         'username': 'TestClient',
#         'password': 'test_password'
#     }

# @pytest_asyncio.fixture
# async def client_create_data():
#     return {
#         "access_token_type": 1,
#         "protocol_type": 1,
#         "refresh_token_expiration_type": 1,
#         "refresh_token_usage_type": 1,
#         "response_types": 1,
#         "client_id": "cli_id",
#         "client_name": "cli_name",
#         "token_endpoint_auth_method": "client_secret_post",
#         "save": "Save"
#     }

# @pytest_asyncio.fixture
# async def access_token_types_create_data():
#     return {
#         "type": "new_access_token_type",
#         "client": 1,
#     }

# @pytest_asyncio.fixture
# async def protocol_types_create_data():
#     return {
#         "type": "new_protocol_type",
#         "client": 1,
#         "save": "Save"
#     }

# @pytest_asyncio.fixture
# async def refresh_token_usage_types_create_data():
#     return {
#         "type": "new_refresh_token_usage_type",
#         "client": 1,
#         "save": "Save"
#     }

# @pytest_asyncio.fixture
# async def refresh_token_expiration_types_create_data():
#     return {
#         "type": "new_refresh_token_expiration_type",
#         "client": 1,
#         "save": "Save"
#     }

# @pytest_asyncio.fixture
# async def client_secrets_create_data():
#     return {
#         'client': 1,
#         'description': 'new_description',
#         'expiration': 1,
#         'type': 'new_type',
#         'value': '18260968-9e17-49a0-aaef-fa39683ffd8f',
#         "save": "Save"
#     }


# @pytest_asyncio.fixture
# async def client_grant_types_create_data():
#     return {
#         'client': 1,
#         'grant_type': 'new_grant_type',
#         "save": "Save"
#     }

# @pytest_asyncio.fixture
# async def client_redirect_uris_create_data():
#     return {
#         'client': 1,
#         'redirect_uri': 'https://new_red_uri.com',
#         "save": "Save"
#     }

# @pytest_asyncio.fixture
# async def client_cors_origins_create_data():
#     return {
#         'client': 1,
#         'origin': 'new_origin',
#         "save": "Save"
#     }

# @pytest_asyncio.fixture
# async def client_post_logout_redirect_uris_create_data():
#     return {
#         'client': 1,
#         'post_logout_redirect_uri': 'https://post_logout_redirect_uri.com',
#         "save": "Save"
#     }

# @pytest_asyncio.fixture
# async def client_claims_create_data():
#     return {
#         'client': 1,
#         'type': 'new_type',
#         'value': 'new_value',
#     }

# @pytest_asyncio.fixture
# async def client_id_restrictions_create_data():
#     return {
#         'client': 1,
#         'provider': 'new_provider',
#     }


@pytest_asyncio.fixture
async def ui_create_data():
    url_data = {
        "identity-provider-mapped": {
            "identity_provider": 1,
            "provider_client_id": 1,
            "provider_client_secret": "new_provider_client_secret",
        },
        "identity-resource": {
            "description": "new_description",
            "display_name": "new_display_name",
            "name": "new_name",
        },
        "identity-claim": {"identity_resource": None, "type": "new_type"},
        "client": {
            "access_token_type": 1,
            "protocol_type": 1,
            "refresh_token_expiration_type": 1,
            "refresh_token_usage_type": 1,
            "response_types": 1,
            "client_id": "cli_id",
            "client_name": "cli_name",
            "token_endpoint_auth_method": "client_secret_post",
            "save": "Save",
        },
        "access-token-type": {
            "type": "new_access_token_type",
        },
        "protocol-type": {"type": "new_protocol_type", "save": "Save"},
        "refresh-token-usage-type": {
            "type": "new_refresh_token_usage_type",
            "save": "Save",
        },
        "refresh-token-expiration-type": {
            "type": "new_refresh_token_expiration_type",
            "save": "Save",
        },
        "client-secret": {
            "client": 1,
            "description": "new_description",
            "expiration": 1,
            "type": "new_type",
            "value": "18260968-9e17-49a0-aaef-fa39683ffd8f",
            "save": "Save",
        },
        "client-grant-type": {
            "client": 1,
            "grant_type": "new_grant_type",
            "save": "Save",
        },
        "client-redirect-uri": {
            "client": 1,
            "redirect_uri": "https://new_red_uri.com",
            "save": "Save",
        },
        "client-cors-origin": {
            "client": 1,
            "origin": "new_origin",
            "save": "Save",
        },
        "client-post-logout-redirect-uri": {
            "client": 1,
            "post_logout_redirect_uri": "https://post_logout_redirect_uri.com",
            "save": "Save",
        },
        "client-claim": {
            "client": 1,
            "type": "new_type",
            "value": "new_value",
        },
        "client-id-restriction": {
            "client": 1,
            "provider": "new_provider",
        },
        "user": {
            "username": "new_user",
        },
        "user-password": {
            "value": "create_password",
        },
        "user-claim": {
            "user": 1,
            "claim_type": 1,
            "claim_value": "new_claim_value",
        },
        "user-claim-type": {
            "type_of_claim": "new_type_of_claim",
        },
        "role": {
            "name": "new_name",
        },
        "group": {
            "name": "new_group",
        },
        "permission": {
            "name": "new_permission",
        },
        "persistent-grant": {
            "client": 1,
            "user": 1,
            "persistent_grant_type": 1,
            "key": "new_key",
            "grant_data": "new_grant_data",
            "expiration": 777,
        },
        "persistent-grant-type": {"type_of_grant": "new_type_of_grant"},
        "api-resource": {
            "description": "new_description",
            "display_name": "new_display_name",
            "enabled": True,
            "name": "new_name",
        },
        "api-secret": {
            "api_resources": None,
            "secret_type": 1,
            "description": "new_description",
            # "expiration": datetime.now() + timedelta(days=1),
            "expiration": "2024-05-20 12:00:0",
            "value": "new_value",
        },
        "api-secret-type": {
            "secret_type": "type",
        },
        "api-claim": {
            "api_resources": None,
            "claim_type": 1,
            "claim_value": "new_claim_value",
        },
        "api-claim-type": {
            "claim_type": "new_claim_type",
        },
        "api-scope": {
            "api_resources": 1,  # depends on Api Resources. Create first
            "description": "new_dscription",
            "name": "new_name",
            "display_name": "new_display_name",
            "emphasize": False,
            "required": False,
            "show_in_discovery_document": False,
        },
        "api-scope-claim": {
            "api_scopes": None,  # don't depend on Api Scope. Create first
            "scope_claim_type": 1,  # ? dependency
        },
        "api-scope-claim-type": {  # 500 Internal Server Error
            "scope_claim_type": "type",
        },
    }
    return url_data


@pytest_asyncio.fixture
async def device_create_data():
    return {
        "client": 1,
        "device_code": "code",
        "user_code": "code",
        "verification_uri": "https://www.device.com",
        "verification_uri_complete": "https://www.device_verif.com",
        "expires_in": 600,
        "interval": 5,
        # "save": "Save"
    }


# @pytest_asyncio.fixture
# async def user_create_data():
#     return {
#         'username': "new_user",
#     }

# @pytest_asyncio.fixture
# async def user_password_create_data():
#     return {
#         'value': "create_password",
#     }

# @pytest_asyncio.fixture
# async def user_claim_create_data():
#     return {
#         'user': 1,
#         'claim_type': 1,
#         'claim_value': "new_claim_value",
#     }

# @pytest_asyncio.fixture
# async def user_claim_type_create_data():
#     return {
#         'type_of_claim': "new_type_of_claim",
#     }


@pytest_asyncio.fixture
async def get_db(connection: AsyncSession) -> None:
    name = "TEST"
    pk = 1000
    # Identity
    await connection.execute(
        delete(IdentityProviderMapped).where(
            IdentityProviderMapped.identity_provider_id == 1
        )
    )
    await connection.flush()
    data = {
        "id": pk,
        "provider_client_id": name,
        "provider_client_secret": name,
        "identity_provider_id": 1,
    }
    await connection.execute(insert(IdentityProviderMapped).values(data))

    data = {
        "id": pk,
        "display_name": name,
        "name": name,
    }
    await connection.execute(insert(IdentityResource).values(data))

    data = {
        "id": pk,
        "identity_resource_id": pk,
        "type": name,
    }
    await connection.execute(insert(IdentityClaim).values(data))

    # Client
    data = {
        "id": pk,
        "client_id": name,
        "client_name": name,
        "access_token_type_id": 1,
        "protocol_type_id": 1,
        "refresh_token_expiration_type_id": 1,
        "refresh_token_usage_type_id": 1,
    }
    await connection.execute(insert(Client).values(data))
    data = {
        "id": pk,
        "type": name,
    }
    await connection.execute(insert(AccessTokenType).values(data))
    await connection.execute(insert(ProtocolType).values(data))
    await connection.execute(insert(RefreshTokenExpirationType).values(data))
    await connection.execute(insert(RefreshTokenUsageType).values(data))

    data = {
        "id": pk,
        "client_id": pk,
        "provider": name,
    }
    await connection.execute(insert(ClientIdRestriction).values(data))

    data = {
        "id": pk,
        "type": name,
        "value": name,
        "client_id": pk,
    }
    await connection.execute(insert(ClientClaim).values(data))

    data = {
        "id": pk,
        "post_logout_redirect_uri": name,
        "client_id": pk,
    }
    await connection.execute(insert(ClientPostLogoutRedirectUri).values(data))

    data = {
        "id": pk,
        "origin": name,
        "client_id": pk,
    }
    await connection.execute(insert(ClientCorsOrigin).values(data))

    data = {
        "id": pk,
        "redirect_uri": name,
        "client_id": pk,
    }
    await connection.execute(insert(ClientRedirectUri).values(data))

    # data = {
    #     "id": pk,
    #     "grant_type": name,
    #     "client_id": pk,
    # }
    # await connection.execute(insert(ClientGrantType).values(data))

    data = {
        "id": pk,
        "description": name,
        "expiration": 121212,
        "type": name,
        "value": name,
        "client_id": pk,
    }
    await connection.execute(insert(ClientSecret).values(data))

    data = {
        "id": pk,
        "client_id": pk,
        "device_code": name,
        "user_code": "a",
        "verification_uri": name,
        "verification_uri_complete": name,
        "expires_in": 123,
        "interval": 123,
    }
    await connection.execute(insert(Device).values(data))

    # User
    data = {
        "id": pk,
        "username": name,
    }
    await connection.execute(insert(User).values(data))

    data = {
        "id": pk,
        "value": name,
    }
    await connection.execute(insert(UserPassword).values(data))

    data = {
        "id": pk,
        "type_of_claim": name,
    }
    await connection.execute(insert(UserClaimType).values(data))

    data = {
        "id": pk,
        "user_id": pk,
        "claim_type_id": pk,
        "claim_value": name,
    }
    await connection.execute(insert(UserClaim).values(data))

    # Groups Roles
    data = {
        "id": pk,
        "name": name,
    }
    await connection.execute(insert(Role).values(data))
    await connection.execute(insert(Group).values(data))
    await connection.execute(insert(Permission).values(data))

    # Tokens
    data = {
        "id": pk,
        "type_of_grant": name,
    }
    await connection.execute(insert(PersistentGrantType).values(data))

    data = {
        "id": pk,
        "key": name,
        "client_id": pk,
        "grant_data": name,
        "expiration": 123123,
        "user_id": pk,
        "persistent_grant_type_id": pk,
    }
    await connection.execute(insert(PersistentGrant).values(data))

    # API
    data = {
        "id": pk,
        "description": name,
        "display_name": name,
        "name": name,
    }
    await connection.execute(insert(ApiResource).values(data))
    data = {
        "id": pk,
        "secret_type": name,
    }
    await connection.execute(insert(ApiSecretType).values(data))
    data = {
        "id": pk,
        "claim_type": name,
    }
    await connection.execute(insert(ApiClaimType).values(data))
    data = {
        "id": pk,
        "scope_claim_type": name,
    }
    await connection.execute(insert(ApiScopeClaimType).values(data))

    data = {
        "id": pk,
        "api_resources_id": pk,
        "description": name,
        "expiration": datetime.date.today(),
        "secret_type_id": pk,
        "value": name,
    }
    await connection.execute(insert(ApiSecret).values(data))

    data = {
        "id": pk,
        "api_resources_id": pk,
        "claim_type_id": pk,
        "claim_value": name,
    }
    await connection.execute(insert(ApiClaim).values(data))

    data = {
        "id": pk,
        "api_resources_id": pk,
        "description": name,
        "name": name,
    }
    await connection.execute(insert(ApiScope).values(data))

    data = {
        "id": pk,
        "api_scopes_id": pk,
        "scope_claim_type_id": pk,
    }
    await connection.execute(insert(ApiScopeClaim).values(data))

    await connection.commit()


@pytest_asyncio.fixture
async def client_service(connection: AsyncSession) -> ClientService:
    client_service = ClientService(
        client_repo=ClientRepository(connection), session=connection
    )
    return client_service
