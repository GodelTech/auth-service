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


class TestUIAdminCreate:
    content_type = "application/x-www-form-urlencoded"
    content_type_form = "multipart/form-data"

    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    async def test_create_api_resource_api_scope(
            self,
            connection: AsyncSession,
            client: AsyncClient,
    ):
        response = await client.request(
            "POST",
            "/admin/api-resource/create",
            data={
                "description": "new_description",
                "display_name": "new_display_name",
                "enabled": True,
                "name": "new_name"
            },
            headers={"Content-Type": self.content_type},
        )
        await connection.commit()
        assert response.status_code == status.HTTP_302_FOUND
        response = await client.request(
            "POST",
            "/admin/api-scope/create",
            data= {
                "api_resources": 1,
                "description": "new_dscription",
                "name": "new_name",
                "display_name": "new_display_name",
                "emphasize": False,
                "required": False,
                "show_in_discovery_document": False,
            },
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_302_FOUND

        resource = await connection.execute(
            select(ApiResource).where(ApiResource.name == "new_name")
        )
        resource = resource.first()[0]        
        scope = await connection.execute(
            select(ApiScope).where(ApiScope.name == "new_name")
        )
        scope = scope.first()[0]
        
        await connection.delete(scope)
        await connection.delete(resource)
        await connection.commit()


    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    @pytest.mark.parametrize(
        "url, Table, column, Table_column",
        [
            ("identity-provider-mapped", IdentityProviderMapped, "provider_client_secret", IdentityProviderMapped.provider_client_secret),
            ("identity-resource", IdentityResource, "name", IdentityResource.name),
            ("identity-claim", IdentityClaim, "type", IdentityClaim.type),
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
            ("persistent-grant", PersistentGrant, "grant_data", PersistentGrant.grant_data),
            ("persistent-grant-type", PersistentGrantType, "type_of_grant", PersistentGrantType.type_of_grant),
            # ("api-resource", ApiResource, "name", ApiResource.name),
            ("api-secret", ApiSecret, "value", ApiSecret.value),
            ("api-secret-type", ApiSecretType, "secret_type", ApiSecretType.secret_type),  # 500 Internal Server Error
            ("api-claim", ApiClaim, "claim_value", ApiClaim.claim_value),
            ("api-claim-type", ApiClaimType, "claim_type", ApiClaimType.claim_type),
            # ("api-scope", ApiScope, "name", ApiScope.name),
            ("api-scope-claim-type", ApiScopeClaimType, "scope_claim_type", ApiScopeClaimType.scope_claim_type),   # 500 Internal Server Error
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
        assert response.status_code == status.HTTP_302_FOUND
        result = await connection.execute(
            select(Table).where(Table_column == ui_create_data[url][column])
        )
        result = result.first()
        assert result is not None, f"New entity into the table \"{Table.__tablename__}\" was not inserted"
        
        await connection.delete(result[0])
        await connection.commit()

    @pytest.mark.asyncio
    async def test_create_not_token(
            self,
            connection: AsyncSession,
            client: AsyncClient,
    ):
        response = await client.post(
            f"/admin/client/create",
            data={
                "access_token_type": 1,
                "protocol_type": 1,
                "refresh_token_expiration_type": 1,
                "refresh_token_usage_type": 1,
                "response_types": 1,
                "client_id": "cli_id_asdasdad",
                "client_name": "cli_nameP_asdasdad",
                "token_endpoint_auth_method": "client_secret_postasdad",
                "save": "Save"
            },
            headers={"Content-Type": self.content_type},
            cookies={"session": "any"}
        )
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        result = await connection.execute(
            select(Client).where(Client.client_id == "cli_id_asdasdad")
        )
        result = result.first()

        assert result is None

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
            select(Device).where(Device.device_code == "code")
        )
        result = result.first()
        assert result is not None, "Device not found"




    @pytest.mark.asyncio
    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    @pytest.mark.parametrize(
        "url, Table",
        [
            ("user-password", UserPassword),
            ("api-scope-claim", ApiScopeClaim),
        ]
    )
    async def test_create_user_password(
            self,
            ui_create_data,
            connection: AsyncSession,
            client: AsyncClient,
            url, Table,
    ):
        rows_before = await connection.execute(select(Table))
        rows_before = rows_before.scalars().all()
        num_rows_before = len(rows_before) if rows_before else 0

        response = await client.post(
            f"/admin/{url}/create",
            data=ui_create_data[url],
            headers={"Content-Type": self.content_type},
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND

        rows_after = await connection.execute(select(Table))
        rows_after = rows_after.scalars().all()
        num_rows_after = len(rows_after) if rows_after else 0
        assert num_rows_after > num_rows_before


