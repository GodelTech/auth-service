import json

import pytest
from fastapi import status
from httpx import AsyncClient

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)


@pytest.mark.asyncio
class TestRevokationEndpoint:
    @pytest.mark.asyncio
    async def test_successful_revoke_request(
        self, engine, token_service, client: AsyncClient
    ):
        persistent_grant_repo = PersistentGrantRepository(engine)
        grant_type = "refresh_token"
        revoke_token = "----token_to_delete-----"

        await persistent_grant_repo.create(
            grant_type=grant_type,
            grant_data=revoke_token,
            user_id=1,
            client_id="test_client",
            expiration_time=3600,
        )
        headers = {
            "authorization": await token_service.jwt_service.encode_jwt(
                payload={"sub": "1"}
            ),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {"token": revoke_token, "token_type_hint": grant_type}
        response = await client.request(
            method="POST", url="/revoke/", data=params, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert not await persistent_grant_repo.exists(
            grant_type=grant_type, grant_data=revoke_token
        )

    @pytest.mark.asyncio
    async def test_token_does_not_exists(
        self, engine, token_service, client: AsyncClient
    ):
        self.persistent_grant_repo = PersistentGrantRepository(engine)

        grant_type = "code"
        revoke_token = "----token_not_exists-----"
        headers = {
            "authorization": await token_service.jwt_service.encode_jwt(
                payload={"sub": "1"}
            ),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        params = {"token": revoke_token, "token_type_hint": grant_type}
        response = await client.request(
            method="POST", url="/revoke/", data=params, headers=headers
        )
        response_content = json.loads(response.content.decode("utf-8"))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_content == {"detail": "Incorrect Token"}

    @pytest.mark.asyncio
    async def test_get_test_token(self, token_service, client: AsyncClient):
        response = await client.request("GET", "/revoke/test_token")
        response_content = json.loads(response.content.decode("utf-8"))
        response_content = await token_service.jwt_service.decode_token(
            token=response_content
        )

        assert response.status_code == status.HTTP_200_OK
        assert response_content == {"sub": "1"}
