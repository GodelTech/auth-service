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
import datetime, time
from mock import patch
from unittest.mock import patch
from src.business_logic.services.admin_auth import AdminAuthService

logger = logging.getLogger(__name__)

async def fake_authenticate(*args, **kwargs):
    return None

@pytest.mark.asyncio
class TestAdminUIDelete:
    async def setup_base(self, connection:AsyncSession, pk: int = 1000) -> None:
        name = 'TEST_DELETE'
        # Identity
        await connection.execute(delete(IdentityProviderMapped).where(IdentityProviderMapped.identity_provider_id == 1))
        await connection.flush()
        data = {
            'id': pk,
            'provider_client_id': name,
            'provider_client_secret':name,
            'identity_provider_id':1,
            }
        await connection.execute(insert(IdentityProviderMapped).values(data))
        
        data = {
            'id': pk,
            'display_name': name,
            'name':name,
        } 
        await connection.execute(insert(IdentityResource).values(data))
          
        data = {
            'id': pk,
            'identity_resource_id': pk,
            'type':name,
        } 
        await connection.execute(insert(IdentityClaim).values(data))
        
        # Client
        data = {
            'id': pk,
            'client_id': name,
            'client_name':name,
            'access_token_type_id':1,
            'protocol_type_id':1,
            'refresh_token_expiration_type_id':1,
            'refresh_token_usage_type_id':1,
            }
        await connection.execute(insert(Client).values(data))
        data = {
            'id': pk,
            'type':name,
            }
        await connection.execute(insert(AccessTokenType).values(data))
        await connection.execute(insert(ProtocolType).values(data))
        await connection.execute(insert(RefreshTokenExpirationType).values(data))
        await connection.execute(insert(RefreshTokenUsageType).values(data))

        data = {
            'id': pk,
            'client_id':pk,
            'provider':name,
            }
        await connection.execute(insert(ClientIdRestriction).values(data))

        data = {
            'id': pk,
            'type':name,
            'value':name,
            'client_id':pk,
            }
        await connection.execute(insert(ClientClaim).values(data))

        data = {
            'id': pk,
            'post_logout_redirect_uri':name,
            'client_id':pk,
            }
        await connection.execute(insert(ClientPostLogoutRedirectUri).values(data))

        data = {
            'id': pk,
            'origin':name,
            'client_id':pk,
            }
        await connection.execute(insert(ClientCorsOrigin).values(data))

        data = {
            'id': pk,
            'redirect_uri':name,
            'client_id':pk,
            }
        await connection.execute(insert(ClientRedirectUri).values(data))

        data = {
            'id': pk,
            'grant_type':name,
            'client_id':pk,
            }
        await connection.execute(insert(ClientGrantType).values(data))

        data = {
            'id': pk,
            'description':name,
            'expiration':121212,
            'type':name,
            'value':name,
            'client_id':pk,
            }
        await connection.execute(insert(ClientSecret).values(data))

        data = {
            'id':pk,
            'client_id':pk,
            'device_code':name,
            'user_code':'a',
            'verification_uri':name,
            'verification_uri_complete':name,
            'expires_in':123,
            'interval':123,
            }
        await connection.execute(insert(Device).values(data))

        # User
        data = {
            'id':pk,
            'username':name,
            }
        await connection.execute(insert(User).values(data))

        data = {
            'id':pk,
            'value':name,
            }
        await connection.execute(insert(UserPassword).values(data))

        data = {
            'id':pk,
            'type_of_claim':name,
            }
        await connection.execute(insert(UserClaimType).values(data))

        data = {
            'id':pk,
            'user_id':pk,
            'claim_type_id':pk,
            'claim_value':name,
            }
        await connection.execute(insert(UserClaim).values(data))

        #Groups Roles
        data = {
            'id':pk,
            'name':name,
            }
        await connection.execute(insert(Role).values(data))
        await connection.execute(insert(Group).values(data))
        await connection.execute(insert(Permission).values(data))

        # Tokens
        data = {
            'id':pk,
            'type_of_grant':name,
            }
        await connection.execute(insert(PersistentGrantType).values(data))
        data = {
            'id':pk,
            'key':name,
            'client_id':pk,
            'grant_data':name,
            'expiration':123123,
            'user_id':pk,
            'persistent_grant_type_id':pk,
            }
        await connection.execute(insert(PersistentGrant).values(data))

        # API
        data = {
            "id": pk,
            "description": name,
            "display_name" : name,
            'name' : name,
            }
        await connection.execute(insert(ApiResource).values(data))
        data = {
            "id": pk,
            "secret_type" : name,
            }
        await connection.execute(insert(ApiSecretType).values(data))
        data = {
            "id": pk,
            "claim_type" : name,
            }
        await connection.execute(insert(ApiClaimType).values(data))
        data = {
            "id": pk,
            "scope_claim_type" : name,
            }
        await connection.execute(insert(ApiScopeClaimType).values(data))
        
        data = {
            "id": pk,
            "api_resources_id" : pk,
            "description":name,
            "expiration":datetime.date.today(),
            "secret_type_id": pk,
            "value": name,
            }
        await connection.execute(insert(ApiSecret).values(data))
        
        data = {
            "id": pk,
            "api_resources_id" : pk,
            "claim_type_id":pk,
            "claim_value": name,
            }
        await connection.execute(insert(ApiClaim).values(data))

        data = {
            "id": pk,
            "api_resources_id" : pk,
            "description":name,
            "name": name,
            }
        await connection.execute(insert(ApiScope).values(data))

        data = {
            "id": pk,
            "api_scopes_id" : pk,
            "scope_claim_type_id":pk,
            }
        await connection.execute(insert(ApiScopeClaim).values(data))

        await connection.commit()

    @patch.object(AdminAuthService, 'authenticate', fake_authenticate)
    async def test_delete(self, connection:AsyncSession, client: AsyncClient) -> None:
        pk = 123456
        await self.setup_base(connection=connection, pk=pk)

        tables_identity =[
            IdentityClaim,
            IdentityResource,
            IdentityProviderMapped
            ]
        tables_cl =[
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
            ]
        tables_user =[
            UserClaim,
            UserClaimType,
            UserPassword, 
            User,
        ]
        tables_groups = [
            Role,
            Permission,
            Group
        ]
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
        
        for tables in tables_all:
            for table in tables:
                part_of_link:str = table.__tablename__
                part_of_link = part_of_link.replace("_", '-')
                part_of_link = part_of_link[:-1]
                
                if part_of_link == 'api-secrets-type':
                    part_of_link = 'api-secret-type'
                if part_of_link == 'identity-providers-mappe':
                    part_of_link = 'identity-provider-mapped'
                if part_of_link == 'client-scope':
                    continue
            
                # print(part_of_link)
                # db_check = (await connection.execute(select(exists().where(table.id == pk)))).first()
                response = await client.request(
                    "DELETE", f"/admin/{part_of_link}/delete?pks={pk}", cookies={"session": '1'}
                )
                assert response.status_code == status.HTTP_200_OK