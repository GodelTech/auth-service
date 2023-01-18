import mock
import json
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from src.business_logic.services.tokens import TokenService
from src.business_logic.services.userinfo import UserInfoServices
from time import sleep
from datetime import datetime
async def new_check_authorisation_token(*args, **kwargs):
    return True


# @pytest.mark.asyncio
class TestIntrospectionEndpoint:

    @pytest.mark.asyncio
    async def test_successful_introspection_request(self, connection: AsyncSession, client: AsyncClient):

            self.jwt = JWTService()
            self.persistent_grant_repo = PersistentGrantRepository(connection)

            grant_type = "code"
            payload = {
                "sub" : 1,
                "expire": "2030-12-19 09:24:14",
            }
            introspection_token = await self.jwt.encode_jwt(payload=payload)

            
            await self.persistent_grant_repo.delete(
                grant_type=grant_type,
                data=introspection_token
            )

            await self.persistent_grant_repo.create(
                grant_type=grant_type,
                data=introspection_token,
                user_id=1,
                client_id="test_client",
                expiration_time=3600,
            )

            headers = {
                "authorization": await self.jwt.encode_jwt(payload={"sub": "1"}),
                "Content-Type": "application/x-www-form-urlencoded"
            }
            params = {
                'token': introspection_token,
                'token_type_hint': grant_type
            }
            answer = {
                "active":True,
                "scope":None,
                "client_id":"test_client",
                "username":"Danya",
                "token_type":"Bearer",
                "exp":0,
                "iat":None,
                "nbf":None,
                "sub":"1",
                "aud":None,
                "iss":"http://testserver",
                "jti":None
                }
            
            response = await client.request(method="POST", url='/introspection/', data=params, headers=headers)
            response_content = json.loads(response.content.decode('utf-8'))
            assert response.status_code == status.HTTP_200_OK
            response_content["exp"] = 0
            assert response_content == answer

    @pytest.mark.asyncio
    async def test_successful_introspection_request_spoiled_token(self, connection: AsyncSession, client: AsyncClient):

            self.jwt = JWTService()
            
            self.persistent_grant_repo = PersistentGrantRepository(connection)

            grant_type = "code"
            payload = {
                "sub" : 1,
                "exp" : datetime.now().timestamp() + 2
            }

            introspection_token = await self.jwt.encode_jwt(payload=payload)
            sleep(2)

            await self.persistent_grant_repo.delete(
                grant_type=grant_type,
                data=introspection_token
            )

            await self.persistent_grant_repo.create(
                grant_type=grant_type,
                data=introspection_token,
                user_id=1,
                client_id="test_client",
                expiration_time=1,
            )
            
            headers = {
                "authorization": await self.jwt.encode_jwt(payload={"sub": "1"}, secret= '123'),
                "Content-Type": "application/x-www-form-urlencoded"
            }

            params = {
                'token': introspection_token,
                'token_type_hint': grant_type
            }

            response = await client.request(method="POST", url='/introspection/', data=params, headers=headers)
            response_content = json.loads(response.content.decode('utf-8'))
            assert response.status_code == status.HTTP_200_OK
            assert response_content["active"] == False
            response_content["active"] = None
            assert set(response_content.values()) == {None}

    # @pytest.mark.asyncio
    # async def test_incorrect_auth(self, connection: AsyncSession, client: AsyncClient):

    #     self.jwt = JWTService()
    #     self.jwt.set_expire_time(expire_hours=1)
    #     self.persistent_grant_repo = PersistentGrantRepository(connection)

    #     grant_type = "code"
    #     payload = {
    #         "sub" : 1,
    #     }

    #     introspection_token = await self.jwt.encode_jwt(payload=payload)

    #     await self.persistent_grant_repo.delete(
    #         grant_type=grant_type,
    #         data=introspection_token
    #     )

    #     await self.persistent_grant_repo.create(
    #         grant_type=grant_type,
    #         data=introspection_token,
    #         user_id=1,
    #         client_id="test_client",
    #         expiration_time=1,
    #     )
        
    #     headers = {
    #         "authorization": await self.jwt.encode_jwt(payload={"sub": "1"}),
    #         "Content-Type": "application/x-www-form-urlencoded"
    #     }

    #     params = {
    #         'token': introspection_token,
    #         'token_type_hint': grant_type
    #     }
  
    #     response = await client.request(method="POST", url='/introspection/', data=params, headers=headers)
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED