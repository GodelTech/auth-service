import json
import mock
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from src.business_logic.services.tokens import TokenService
from src.business_logic.services.userinfo import UserInfoServices


async def new_check_authorisation_token(*args, **kwargs):
    return True


@pytest.mark.asyncio
class TestRevokationEndpoint:

    # @pytest.mark.asyncio
    async def test_successful_revoke_request(self, connection: AsyncSession, client: AsyncClient):

            self.jwt = JWTService()
            self.persistent_grant_repo = PersistentGrantRepository(connection)

            grant_type = "code"
            #await self.jwt.encode_jwt(payload={"sub":1})
            revoke_token = "----token_to_delete-----"

            await self.persistent_grant_repo.delete(
                grant_type=grant_type,
                data=revoke_token
            )

            await self.persistent_grant_repo.create(
                grant_type=grant_type,
                data=revoke_token,
                user_id=1,
                client_id="test_client",
                expiration_time=3600,
            )

            headers = {
                "authorization": await self.jwt.encode_jwt(payload={"sub": "1"}),
                "Content-Type": "application/x-www-form-urlencoded"
            }

            params = {
                'token': revoke_token,
                'token_type_hint': grant_type
            }

            response = await client.request(method="POST", url='/revoke/', data=params, headers=headers)
            assert response.status_code == status.HTTP_200_OK
            assert not await self.persistent_grant_repo.exists(grant_type="code", data=revoke_token)

    # @pytest.mark.asyncio
    # async def test_incorrect_auth(self, connection: AsyncSession, client: AsyncClient):

    #     self.persistent_grant_repo = PersistentGrantRepository(connection)
    #     grant_type = "code"
    #     # await self.jwt.encode_jwt(payload={"sub":1})
    #     revoke_token = "----token_to_delete-----"

    #     await self.persistent_grant_repo.delete(
    #         grant_type=grant_type,
    #         data=revoke_token
    #     )

    #     await self.persistent_grant_repo.create(
    #         grant_type=grant_type,
    #         data=revoke_token,
    #         user_id=1,
    #         client_id="test_client",
    #         expiration_time=3600,
    #     )
    
    #     headers = {
    #         "authorization": "incorrect_token",
    #         "Content-Type": "application/x-www-form-urlencoded"
    #     }

    #     params = {
    #         'token': revoke_token,
    #         'token_type_hint': grant_type
    #     }

    #     response = await client.request(method="POST", url='/revoke/', data=params, headers=headers)
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    #     await self.persistent_grant_repo.delete(
    #         grant_type=grant_type,
    #         data=revoke_token
    #     )

    @pytest.mark.asyncio
    async def test_token_does_not_exists(self, connection: AsyncSession, client: AsyncClient):

            self.jwt = JWTService()
            self.persistent_grant_repo = PersistentGrantRepository(connection)

            grant_type = "code"
            #await self.jwt.encode_jwt(payload={"sub":1})
            revoke_token = "----token_not_exists-----"

            await self.persistent_grant_repo.delete(
                grant_type=grant_type,
                data=revoke_token
            )

            headers = {
                "authorization": await self.jwt.encode_jwt(payload={"sub": "1"}),
                "Content-Type": "application/x-www-form-urlencoded"
            }

            params = {
                'token': revoke_token,
                'token_type_hint': grant_type
            }

            response = await client.request(method="POST", url='/revoke/', data=params, headers=headers)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
