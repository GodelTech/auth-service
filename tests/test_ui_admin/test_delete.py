import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, exists, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
import logging
from typing import Any
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
from mock import patch
from unittest.mock import patch
from src.business_logic.services.admin_auth import AdminAuthService

logger = logging.getLogger(__name__)


async def fake_authenticate(*args, **kwargs):
    return None


@pytest.mark.asyncio
class TestAdminUIDelete:
    tables_identity = [
        IdentityClaim,
        IdentityResource,
        IdentityProviderMapped,
    ]
    tables_cl = [
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
    ]
    tables_user = [
        UserClaim,
        UserClaimType,
        UserPassword,
        User,
    ]
    tables_groups = [Role, Permission, Group]
    tables_api = [
        ApiScopeClaim,
        ApiScope,
        ApiClaim,
        ApiSecret,
        ApiScopeClaimType,
        ApiClaimType,
        ApiSecretType,
        ApiResource,
    ]
    tables_tokens = [
        PersistentGrant,
        PersistentGrantType,
    ]

    tables_all = [
        tables_tokens,
        tables_api,
        tables_cl,
        tables_groups,
        tables_user,
        tables_identity,
    ]

    @patch.object(AdminAuthService, "authenticate", fake_authenticate)
    async def test_delete_successful(self, get_db, client: AsyncClient) -> None:
        for tables in self.tables_all:
            for table in tables:
                part_of_link: str = table.__tablename__
                part_of_link = part_of_link.replace("_", "-")
                part_of_link = part_of_link[:-1]

                if part_of_link == "api-secrets-type":
                    part_of_link = "api-secret-type"
                if part_of_link == "identity-providers-mappe":
                    part_of_link = "identity-provider-mapped"
                if part_of_link == "client-scope":
                    continue

                response = await client.request(
                    "DELETE",
                    f"/admin/{part_of_link}/delete?pks=1000",
                    cookies={"session": "1"},
                )
                assert response.status_code == status.HTTP_200_OK

    async def test_delete_unsuccessful(
        self, get_db, client: AsyncClient
    ) -> None:
        for tables in self.tables_all:
            for table in tables:
                part_of_link: str = table.__tablename__
                part_of_link = part_of_link.replace("_", "-")
                part_of_link = part_of_link[:-1]

                if part_of_link == "api-secrets-type":
                    part_of_link = "api-secret-type"
                if part_of_link == "identity-providers-mappe":
                    part_of_link = "identity-provider-mapped"
                if part_of_link == "client-scope":
                    continue

                response = await client.request(
                    "DELETE",
                    f"/admin/{part_of_link}/delete?pks=1000",
                    cookies={"session": "1"},
                )
                assert (
                    response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
                )
