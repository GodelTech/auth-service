import time
import json
import pytest

from fastapi import status
from httpx import AsyncClient

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories import UserRepository, PersistentGrantRepository


async def new_check_authorisation_token(*args, **kwargs):
    return True


# @pytest.mark.asyncio
class TestIntrospectionEndpoint:

    @pytest.mark.asyncio
    async def test_successful_introspection_request(self, engine, client: AsyncClient):
        jwt = JWTService()
        persistent_grant_repo = PersistentGrantRepository(engine)
        user_repo = UserRepository(engine)

        grant_type = "code"
        payload = {
            "sub": 1,
            "exp": time.time() + 3600,
            "client_id": "test_client"
        }
        introspection_token = await jwt.encode_jwt(payload=payload)
        access_token = await jwt.encode_jwt(payload={"sub": "1", "client_id": "test_client"})

        await persistent_grant_repo.delete(
            grant_type = "refresh_token", 
            grant_data=introspection_token
        )

        await persistent_grant_repo.create(
            grant_type='code',
            grant_data=introspection_token,
            user_id=1,
            client_id="test_client",
            expiration_time=3600,
        )

        headers = {
            "authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        params = {
            'token': introspection_token,
            'token_type_hint': grant_type
        }

        user = await user_repo.get_user_by_id(user_id=1)
        answer = {
            "active": True,
            "scope": None,
            "client_id": "test_client",
            "username": user.username,
            "token_type": "Bearer",
            "exp": 0,
            "iat": None,
            "nbf": None,
            "sub": "1",
            "aud": None,
            "iss": "http://testserver",
            "jti": None
        }

        response = await client.request(method="POST", url='/introspection/', data=params, headers=headers)
        response_content = json.loads(response.content.decode('utf-8'))
        assert response.status_code == status.HTTP_200_OK
        response_content["exp"] = 0
        assert response_content == answer

        await persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(user_id=1, client_id="test_client")

    @pytest.mark.asyncio
    async def test_successful_introspection_request_spoiled_token(self, engine, client: AsyncClient):
        jwt = JWTService()
        persistent_grant_repo = PersistentGrantRepository(engine)

        grant_type = "code"
        payload = {
            "sub": 1,
            "exp": time.time()
        }

        introspection_token = await jwt.encode_jwt(payload=payload)

        await persistent_grant_repo.delete(
            grant_type=grant_type,
            grant_data=introspection_token
        )

        await persistent_grant_repo.create(
            grant_type=grant_type,
            grant_data=introspection_token,
            user_id=1,
            client_id="test_client",
            expiration_time=1,
        )

        headers = {
            "authorization": await jwt.encode_jwt(payload={"sub": "1"}),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        params = {
            'token': introspection_token,
            'token_type_hint': grant_type
        }

        response = await client.request(method="POST", url='/introspection/', data=params, headers=headers)
        response_content = json.loads(response.content.decode('utf-8'))
        assert response.status_code == status.HTTP_200_OK
        assert response_content["active"] is False
        response_content["active"] = None
        assert set(response_content.values()) == {None}

        await persistent_grant_repo.delete(
            grant_type=grant_type,
            grant_data=introspection_token
        )
