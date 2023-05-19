import json
import time

import pytest
import pytest_asyncio
from fastapi import status

from unittest.mock import patch

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
    ClientGrantType,
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

from src.business_logic.services.admin_auth import AdminAuthService

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from src.business_logic.services import JWTService

async def fake_authenticate(*args, **kwargs):
    return None



# class TestUIAdminLogin:
#     content_type = "application/x-www-form-urlencoded"
#
#     @pytest.mark.asyncio
#     async def test_get_login(
#             self, connection: AsyncSession,
#             client: AsyncClient
#     ):
#         get_response = await client.get(
#             "/admin/login"
#         )
#         assert get_response.status_code == status.HTTP_200_OK
#
#     @pytest.mark.asyncio
#     async def test_post_cookies_session_token(
#             self, admin_credentials,
#             connection: AsyncSession,
#             client: AsyncClient
#     ):
#         auth_response = await client.post(
#             "/admin/login",
#             data=admin_credentials,
#             headers={"Content-Type": self.content_type},
#         )
#         assert auth_response.status_code == status.HTTP_302_FOUND
#         cookies = auth_response.cookies
#         session_cookie = auth_response.cookies.get('session')
#         assert cookies
#         assert session_cookie
#
#
# class TestUIAdminClient:
#
#     @pytest.mark.asyncio
#     async def test_get_login(self, admin_credentials, connection: AsyncSession, client: AsyncClient):
#
#         get_response = await client.get(
#             "/admin/login",
#         )
#         assert get_response.status_code == status.HTTP_200_OK

#
# class TestUIAdminRead:
#     content_type = "application/x-www-form-urlencoded"
#     @pytest.mark.asyncio
#     @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
#     async def test_get_client(self, admin_credentials, connection: AsyncSession, client: AsyncClient):
#
#         response = await client.get(
#             "/admin/client/list",
#             # cookies={"session": session_cookie},
#             headers={"Content-Type": self.content_type},
#         )
#
#         assert response.status_code == status.HTTP_200_OK

class TestUIAdminCreate:
    content_type = "application/x-www-form-urlencoded"
    content_type_form = "multipart/form-data"

    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client(
    #         self,
    #         client_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #
    #     response = await client.post(
    #         "/admin/client/create",
    #         data=client_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(Client).where(Client.client_id == client_create_data['client_id'])
    #     )
    #     result = result.first()
    #     assert result is not None, "Client not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_access_token_type(
    #         self,
    #         access_token_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/access-token-type/create",
    #         data=access_token_types_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(AccessTokenType).where(AccessTokenType.type == access_token_types_create_data['type'])
    #     )
    #     result = result.first()
    #     assert result is not None, "AccessTokenType not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_protocol_type(
    #         self,
    #         protocol_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/protocol-type/create",
    #         data=protocol_types_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(ProtocolType).where(ProtocolType.type == "new_protocol_type")
    #     )
    #     result = result.first()
    #     assert result is not None, "ProtocolType not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_refresh_token_usage_type(
    #         self,
    #         refresh_token_usage_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/refresh-token-usage-type/create",
    #         data=refresh_token_usage_types_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(RefreshTokenUsageType).where(RefreshTokenUsageType.type == "new_refresh_token_usage_type")
    #     )
    #     result = result.first()
    #     assert result is not None, "RefreshTokenUsageType not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_refresh_token_expiration_type(
    #         self,
    #         refresh_token_expiration_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/refresh-token-expiration-type/create",
    #         data=refresh_token_expiration_types_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(RefreshTokenExpirationType).where(RefreshTokenExpirationType.type == "new_refresh_token_expiration_type")
    #     )
    #     result = result.first()
    #     assert result is not None, "RefreshTokenExpirationType not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client_secrets(
    #         self,
    #         client_secrets_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/client-secret/create",
    #         data=client_secrets_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(ClientSecret).where(ClientSecret.type == "new_type")
    #     )
    #     result = result.first()
    #     assert result is not None, "ClientSecret not found"
    #
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client_grant_types(
    #         self,
    #         client_grant_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/client-grant-type/create",
    #         data=client_grant_types_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(ClientGrantType).where(ClientGrantType.grant_type == "new_grant_type")
    #     )
    #     result = result.first()
    #     assert result is not None, "ClientGrantType not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client_redirect_uri(
    #         self,
    #         client_redirect_uris_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/client-redirect-uri/create",
    #         data=client_redirect_uris_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(ClientRedirectUri).where(ClientRedirectUri.redirect_uri == "https://new_red_uri.com")
    #     )
    #     result = result.first()
    #     assert result is not None, "ClientRedirectUri not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client_cors_origin(
    #         self,
    #         client_cors_origins_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/client-cors-origin/create",
    #         data=client_cors_origins_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(ClientCorsOrigin).where(ClientCorsOrigin.origin == "new_origin")
    #     )
    #     result = result.first()
    #     assert result is not None, "ClientCorsOrigin not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client_post_logout_redirect_uri(
    #         self,
    #         client_post_logout_redirect_uris_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/client-post-logout-redirect-uri/create",
    #         data=client_post_logout_redirect_uris_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(ClientPostLogoutRedirectUri).where(
    #             ClientPostLogoutRedirectUri.post_logout_redirect_uri == "https://post_logout_redirect_uri.com")
    #     )
    #     result = result.first()
    #     assert result is not None, "ClientPostLogoutRedirectUri not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client_claim(
    #         self,
    #         client_claims_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/client-claim/create",
    #         data=client_claims_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(ClientClaim).where(ClientClaim.type == "new_type")
    #     )
    #     result = result.first()
    #     assert result is not None, "ClientClaim not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client_id_restriction(
    #         self,
    #         client_id_restrictions_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/client-id-restriction/create",
    #         data=client_id_restrictions_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(ClientIdRestriction).where(ClientIdRestriction.provider == "new_provider")
    #     )
    #     result = result.first()
    #     assert result is not None, "ClientIdRestriction not found"

    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    @pytest.mark.parametrize(
        "url, Table, column, Table_column",
        [
            ("client", Client, "client_id", Client.client_id),
            ("access-token-type", AccessTokenType, "type", AccessTokenType.type),
            ("protocol-type", ProtocolType, "type", ProtocolType.type),
            ("refresh-token-usage-type", RefreshTokenUsageType, "type", RefreshTokenUsageType.type),
            ("refresh-token-expiration-type", RefreshTokenExpirationType, "type", RefreshTokenExpirationType.type),
            ("client-secret", ClientSecret, "type", ClientSecret.type),
            ("client-grant-type", ClientGrantType, "grant_type", ClientGrantType.grant_type),
            ("client-redirect-uri", ClientRedirectUri, "redirect_uri", ClientRedirectUri.redirect_uri),
            ("client-cors-origin", ClientCorsOrigin, "origin", ClientCorsOrigin.origin),
            ("client-post-logout-redirect-uri", ClientPostLogoutRedirectUri, "post_logout_redirect_uri",
             ClientPostLogoutRedirectUri.post_logout_redirect_uri),
            ("client-claim", ClientClaim, "type", ClientClaim.type),
            ("client-id-restriction", ClientIdRestriction, "provider", ClientIdRestriction.provider),
            ("user", User, "username", User.username),
            ("user-claim", UserClaim, "claim_value", UserClaim.claim_value),
            ("user-claim-type", UserClaimType, "type_of_claim", UserClaimType.type_of_claim),
            ("role", Role, "name", Role.name),
            ("group", Group, "name", Group.name),
            ("permission", Permission, "name", Permission.name),
        ]
    )
    async def test_create_all_user_role_client(
            self,
            ui_create_data,
            connection: AsyncSession,
            client: AsyncClient,
            url, Table, column, Table_column,
    ):
        response = await client.post(
            f"/admin/{url}/create",
            data=ui_create_data[url],
            headers={"Content-Type": self.content_type},
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND, f"Error in the table \"{Table.__tablename__}\" "
        result = await connection.execute(
            select(Table).where(Table_column == ui_create_data[url][column])
        )
        result = result.first()
        assert result is not None, f"New entity into the table \"{Table.__tablename__}\" was not inserted"

    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    async def test_create_device(
            self,
            device_create_data,
            connection: AsyncSession,
            client: AsyncClient,
    ):
        response = await client.post(
            "/admin/device/create",
            data=device_create_data,
            headers={"Content-Type": self.content_type},
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND
        result = await connection.execute(
            select(Device).where(Device.device_code == "device_code_example")
        )
        result = result.first()
        assert result is not None, "Device not found"


    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_user(
    #         self,
    #         user_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/user/create",
    #         data=user_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(User).where(User.username == "new_user")
    #     )
    #     result = result.first()
    #     assert result is not None, "User not found"
    #
    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    async def test_create_user_password(
            self,
            ui_create_data,
            connection: AsyncSession,
            client: AsyncClient,
    ):
        rows_before = await connection.execute(select(UserPassword))
        rows_before = rows_before.scalars().all()
        num_rows_before = len(rows_before) if rows_before else 0

        response = await client.post(
            "/admin/user-password/create",
            data=ui_create_data["user-password"],
            headers={"Content-Type": self.content_type},
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND

        rows_after = await connection.execute(select(UserPassword))
        rows_after = rows_after.scalars().all()
        num_rows_after = len(rows_after) if rows_after else 0
        assert num_rows_after > num_rows_before

    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_user_claim(
    #         self,
    #         user_claim_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/user-claim/create",
    #         data=user_claim_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(UserClaim).where(UserClaim.claim_value == "new_claim_value")
    #     )
    #     result = result.first()
    #     assert result is not None, "UserClaim not found"
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_user_claim_type(
    #         self,
    #         user_claim_type_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    # ):
    #     response = await client.post(
    #         "/admin/user-claim-type/create",
    #         data=user_claim_type_create_data,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #     result = await connection.execute(
    #         select(UserClaimType).where(UserClaimType.type_of_claim == "new_type_of_claim")
    #     )
    #     result = result.first()
    #     assert result is not None, "UserClaimType not found"






