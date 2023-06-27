import json
import time

import pytest
from fastapi import status
from httpx import AsyncClient
from typing import Any
from src.di.providers import provide_jwt_manager
from src.data_access.postgresql.repositories import (
    UserRepository,
    PersistentGrantRepository,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession


async def new_check_authorisation_token(*args: Any, **kwargs: Any) -> bool:
    return True


# @pytest.mark.asyncio
class TestIntrospectionEndpoint:
    @pytest.mark.asyncio
    async def test_successful_introspection_request(
        self, connection: AsyncSession, client: AsyncClient
    ) -> None:
        jwt = provide_jwt_manager()
        persistent_grant_repo = PersistentGrantRepository(connection)
        grant_type = "authorization_code"
        payload = {
            "sub": 1,
            "exp": time.time() + 3600,
            "client_id": "test_client",
            "aud": ["introspection"],
        }
        introspection_token = await jwt.encode(payload=payload)
        access_token = await jwt.encode(
            payload={
                "sub": "1",
                "client_id": "test_client",
                "aud": ["introspection"],
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
            # temporary solution, relying on the fact that client with id 1
            # will always have username "TonyStark", which is not true
            # "username": "TonyStark",
            "token_type": "Bearer",
            "exp": 0,
            "iat": None,
            "nbf": None,
            "sub": "1",
            "iss": "http://testserver",
            "jti": None,
            "aud": ["introspection"],
        }
        response = await client.request(
            method="POST", url="/introspection/", data=params, headers=headers
        )
        response_content = json.loads(response.content.decode("utf-8"))
        response_content["exp"] = 0

        assert response.status_code == status.HTTP_200_OK

        # Checking that all the keys and values that are in the expected result
        # persists in the response
        for key, value in expected_result.items():
            assert response_content[key] == value

        # assert response_content == expected_result

    @pytest.mark.asyncio
    async def test_successful_introspection_request_spoiled_token(
        self, connection: AsyncSession, client: AsyncClient
    ) -> None:
        jwt = provide_jwt_manager()
        persistent_grant_repo = PersistentGrantRepository(connection)
        grant_type = "authorization_code"
        payload = {"sub": 1, "exp": time.time(), "aud": ["introspection"]}
        introspection_token = await jwt.encode(payload=payload)

        await persistent_grant_repo.create(
            grant_type=grant_type,
            grant_data=introspection_token,
            user_id=1,
            client_id="test_client",
            expiration_time=1,
        )
        headers = {
            "authorization": await jwt.encode(
                payload={"sub": "1", "aud": ["introspection"]}
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
        self, connection: AsyncSession, client: AsyncClient
    ) -> None:
        jwt = provide_jwt_manager()
        persistent_grant_repo = PersistentGrantRepository(connection)
        grant_type = "authorization_code"
        payload = {
            "sub": 1,
            "exp": time.time() + 3600,
            "client_id": "test_client",
            "aud": ["introspection"],
        }
        introspection_token = await jwt.encode(payload=payload)
        access_token = await jwt.encode(
            payload={
                "sub": "1",
                "client_id": "test_client",
                "aud": ["introspection"],
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
        params = {"token": "incorrect token", "token_type_hint": grant_type}
        response = await client.request(
            method="POST", url="/introspection/", data=params, headers=headers
        )
        response_content = json.loads(response.content.decode("utf-8"))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_content == {"detail": "Incorrect Token"}
