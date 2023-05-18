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
    jwt_service = JWTService()
    content_type = "application/x-www-form-urlencoded"
    content_type_form = "multipart/form-data"
    content_type_from_browser = "multipart/form-data; boundary=---------------------------421146244922359077422924845103"

    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    async def test_create_client(
            self,
            client_create_data,
            connection: AsyncSession,
            client: AsyncClient,
            token: JWTService,
            # admin_credentials
    ):

        response = await client.post(
            "/admin/client/create",
            data=client_create_data,
            headers={"Content-Type": self.content_type},
            # cookies={"session": token},        # don't required
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND
        result = await connection.execute(select(Client).where(Client.client_id == "cli_id"))
        client = result.first()
        assert client is not None, "Client not found"

        # data = {
        #     'id': 9999,
        #     'client_id': "new_id",
        #     'client_name': "new_name",
        #     'access_token_type_id': 1,
        #     'protocol_type_id': 1,
        #     'refresh_token_expiration_type_id': 1,
        #     'refresh_token_usage_type_id': 1,
        # }
        # # await connection.execute(insert(Client).values(data))
        # res2 = await connection.execute(select(Client).where(Client.client_id == "new_id"))
        # cl2 = res2.first()
        # assert cl2 is not None, "Client not found"

    #
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_access_token_type(
    #         self,
    #         access_token_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    #         admin_credentials
    # ):
    #     data = {
    #         "type": "new_access_token_type",
    #         "client": 5,
    #         # "save": "Save"
    #     }
    #
    #     response = await client.post(
    #         "/admin/access-token-type/create",
    #         data=data,
    #         headers={"Content-Type": self.content_type},
    #         # cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #
    # @pytest.mark.asyncio
    # async def test_create_protocol_type(
    #         self,
    #         protocol_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/protocol-type/create",
    #         data=protocol_types_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #
    # @pytest.mark.asyncio
    # async def test_create_refresh_token_usage_type(
    #         self,
    #         refresh_token_usage_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/refresh-token-usage-type/create",
    #         data=refresh_token_usage_types_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #
    # @pytest.mark.asyncio
    # async def test_create_refresh_token_expiration_type(
    #         self,
    #         refresh_token_expiration_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/refresh-token-expiration-type/create",
    #         data=refresh_token_expiration_types_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND

    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client_secrets(
    #         self,
    #         client_secrets_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/client-secret/create",
    #         data=client_secrets_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND

    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    async def test_create_user(
            self,
            user_create_data,
            connection: AsyncSession,
            client: AsyncClient,
            token: JWTService,
    ):
        response = await client.post(
            "/admin/user/create",
            data=user_create_data,
            headers={"Content-Type": self.content_type},
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND
        result = await connection.execute(
            select(User).where(User.username == "new_user")
        )
        user = result.first()
        assert user is not None, "User not found"

    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    async def test_create_user(
            self,
            user_create_data,
            connection: AsyncSession,
            client: AsyncClient,
            token: JWTService,
    ):
        response = await client.post(
            "/admin/user/create",
            data=user_create_data,
            headers={"Content-Type": self.content_type},
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND
        result = await connection.execute(
            select(User).where(User.username == "new_user")
        )
        user = result.first()
        assert user is not None, "User not found"

    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    async def test_create_user_password(
            self,
            user_password_create_data,
            connection: AsyncSession,
            client: AsyncClient,
            token: JWTService,
    ):
        rows_before = await connection.execute(select(UserPassword))
        rows_before = rows_before.scalars().all()
        num_rows_before = len(rows_before) if rows_before else 0

        response = await client.post(
            "/admin/user-password/create",
            data=user_password_create_data,
            headers={"Content-Type": self.content_type},
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND

        rows_after = await connection.execute(select(UserPassword))
        rows_after = rows_after.scalars().all()
        num_rows_after = len(rows_after) if rows_after else 0
        assert num_rows_after > num_rows_before

        # @pytest.mark.asyncio
    # async def test_create_client_grant_types(
    #         self,
    #         client_grant_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/client-grant-type/create",
    #         data=client_grant_types_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #
    # @pytest.mark.asyncio
    # async def test_create_client_redirect_uri(
    #         self,
    #         client_redirect_uris_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/client-redirect-uri/create",
    #         data=client_redirect_uris_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #
    # @pytest.mark.asyncio
    # async def test_create_client_cors_origin(
    #         self,
    #         client_cors_origins_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/client-cors-origin/create",
    #         data=client_cors_origins_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #
    #
    # @pytest.mark.asyncio
    # async def test_create_client_post_logout_redirect_uri(
    #         self,
    #         client_post_logout_redirect_uris_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/client-post-logout-redirect-uri/create",
    #         data=client_post_logout_redirect_uris_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #
    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_client_claim(
    #         self,
    #         client_claims_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/client-claim/create",
    #         data=client_claims_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #
    # @pytest.mark.asyncio
    # async def test_create_client_id_restriction(
    #         self,
    #         client_id_restrictions_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/client-id-restriction/create",
    #         data=client_id_restrictions_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #
    #
    #
    #
    # @pytest.mark.asyncio
    # async def test_create_device(
    #         self,
    #         device_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    # ):
    #     response = await client.post(
    #         "/admin/device/create",
    #         data=device_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies={"session": token},
    #     )
    #     await connection.flush()
    #     assert response.status_code == status.HTTP_302_FOUND
    #



    # @pytest.mark.asyncio
    # async def test_create_device(
    #         self, device_create_data,
    #         admin_credentials,
    #         connection: AsyncSession,
    #         client: AsyncClient
    # ):
    #     auth_response = await client.post(
    #         "http://127.0.0.1:8000/admin/login",
    #         data=admin_credentials,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     assert auth_response.status_code == status.HTTP_302_FOUND
    #     cookies = auth_response.cookies
    #     session_cookie = auth_response.cookies.get('session')
    #     assert cookies
    #     assert session_cookie
    #
    #     response = await client.post(
    #         "http://127.0.0.1:8000/admin/device/create",
    #         data=device_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies=cookies,
    #     )
    #     # print(f"############### PRINT1 ########################")
    #     # print(response.text)
    #     assert response.status_code == 200

        # If the server returns the created device in the response, you can also check the returned data
        # created_device = response.json()
        #
        # assert created_device['client'] == device_data['client']
        # assert created_device['device_code'] == device_data['device_code']
        # assert created_device['user_code'] == device_data['user_code']





##############################################
############# from Daniil ####################
##############################################

# class DanikDurakError(Exception):
#     pass
#
# class TestUIAdminDanik:
#     jwt_service = JWTService()
#     content_type = "application/x-www-form-urlencoded"
#
#     @pytest.mark.asyncio
#     @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
#     async def test_create_client(
#             self,
#             client_create_data,
#             connection: AsyncSession,
#             client: AsyncClient,
#             token: JWTService,
#             # admin_credentials
#     ):
#
#         response = await client.post(
#             "/admin/client/create",
#             data=client_create_data,
#             headers={"Content-Type": self.content_type},
#             # cookies={"session": token},        # don't required
#         )
#         await connection.commit()
#         assert response.status_code == status.HTTP_302_FOUND

    # @pytest.mark.asyncio
    # @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    # async def test_create_access_token_type(
    #         self,
    #         access_token_types_create_data,
    #         connection: AsyncSession,
    #         client: AsyncClient,
    #         token: JWTService,
    #         admin_credentials
    # ):
    #     data = {
    #         "type": "new_access_token_type",
    #         "client": 5,
    #         # "save": "Save"
    #     }
    #
    #     flag = False
    #     err_counter = 0
    #     while flag:
    #         response = await client.post(
    #             "/admin/access-token-type/create",
    #             data=data,
    #             headers={"Content-Type": self.content_type},
    #             # cookies={"session": token},
    #         )
    #         if response.status_code == 400:
    #             err_counter += 1
    #             if err_counter > 10:
    #                 raise DanikDurakError
    #         else:
    #             assert response.status_code == status.HTTP_302_FOUND
    #
    #     # await connection.flush()
    #     # assert response.status_code == status.HTTP_302_FOUND