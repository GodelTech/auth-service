import json
import time

import pytest
from fastapi import status
from httpx import AsyncClient
from typing import Any
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories import UserRepository, PersistentGrantRepository
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession


async def new_check_authorisation_token(*args:Any, **kwargs:Any)-> bool:
    return True


# @pytest.mark.asyncio
class TestIntrospectionEndpoint:
    @pytest.mark.asyncio
    async def test_successful_introspection_request(self, engine: AsyncEngine, client: AsyncClient) -> None:
        jwt = JWTService()
        persistent_grant_repo = PersistentGrantRepository(engine)
        grant_type = "code"
        payload = {
            "sub": 1,
            "exp": time.time() + 3600,
            "client_id": "test_client",
        }
        introspection_token = await jwt.encode_jwt(
            payload=payload
        )
        access_token = await jwt.encode_jwt(
            payload={
                "sub": "1", 
                "client_id": "test_client",
                "aud":["introspection"]
            }
        )
        await persistent_grant_repo.create(
            grant_type=grant_type,
            grant_data=introspection_token,
            user_id=1,
            client_id="test_client",
            expiration_time=3600,
        )
        headers = {
            "authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {"token": introspection_token, "token_type_hint": grant_type}
        expected_result = {
            "active": True,
            "scope": None,
            "client_id": "test_client",
            "username": "TestClient",
            "token_type": "Bearer",
            "exp": 0,
            "iat": None,
            "nbf": None,
            "sub": "1",
            "aud": None,
            "iss": "http://testserver",
            "jti": None,
        }
        response = await client.request(
            method="POST", url="/introspection/", data=params, headers=headers
        )
        response_content = json.loads(response.content.decode("utf-8"))
        response_content["exp"] = 0

        assert response.status_code == status.HTTP_200_OK
        assert response_content == expected_result

    @pytest.mark.asyncio
    async def test_successful_introspection_request_spoiled_token(self, engine: AsyncEngine, client: AsyncClient) -> None:
        jwt = JWTService()
        persistent_grant_repo = PersistentGrantRepository(engine)
        grant_type = "code"
        payload = {"sub": 1, "exp": time.time(), "aud":["introspection"]}
        introspection_token = await jwt.encode_jwt(
            payload=payload
        )

        await persistent_grant_repo.create(
            grant_type=grant_type,
            grant_data=introspection_token,
            user_id=1,
            client_id="test_client",
            expiration_time=1,
        )
        headers = {
            "authorization": await jwt.encode_jwt(
                payload={"sub": "1", "aud":["introspection"]}
            ),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {"token": introspection_token, "token_type_hint": grant_type}

        response = await client.request(
            method="POST", url="/introspection/", data=params, headers=headers
        )
        response_content = json.loads(response.content.decode("utf-8"))
        assert response.status_code == status.HTTP_200_OK
        assert response_content["active"] is False
        response_content["active"] = None
        assert set(response_content.values()) == {None}

    @pytest.mark.asyncio
    async def test_unsuccessful_introspection_request_incorrect_token(
        self, engine: AsyncEngine,  client: AsyncClient
    ) -> None:
        jwt = JWTService()
        persistent_grant_repo = PersistentGrantRepository(engine)
        grant_type = "code"
        payload = {
            "sub": 1,
            "exp": time.time() + 3600,
            "client_id": "test_client",
        }
        introspection_token = await jwt.encode_jwt(
            payload=payload
        )
        access_token = await jwt.encode_jwt(
            payload={"sub": "1", "client_id": "test_client", "aud":["introspection"]}
        )
        await persistent_grant_repo.create(
            grant_type=grant_type,
            grant_data=introspection_token,
            user_id=1,
            client_id="test_client",
            expiration_time=3600,
        )
        headers = {
            "authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {"token": "incorrect token", "token_type_hint": grant_type}
        response = await client.request(
            method="POST", url="/introspection/", data=params, headers=headers
        )
        response_content = json.loads(response.content.decode("utf-8"))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_content == {"detail": "Incorrect Token"}
