import json
import time

import time
import pytest
from fastapi import status
from httpx import AsyncClient, Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.tokens import TokenService
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)


@pytest.mark.asyncio
class TestTokenEndpoint:
    jwt_service = JWTService()
    refresh_token = None
    content_type = "application/x-www-form-urlencoded"

    @pytest.mark.asyncio
    async def test_code_authorization(
        self,
        client: AsyncClient,
        connection: AsyncSession,
        token_service: TokenService,
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        service = token_service
        await service.persistent_grant_repo.create(
            client_id="double_test",
            grant_data="secret_code",
            user_id=1,
            grant_type="authorization_code",
            expiration_time=time.time() + 3600,
            scope='openid'
        )
        await connection.commit()
        params = {
            "client_id": "double_test",
            "grant_type": "authorization_code",
            "code": "secret_code",
            "scope": "openid",
            "redirect_uri": "http://127.0.0.1:8888/callback/",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        refresh_token = response_json["refresh_token"]
        assert (
            await service.persistent_grant_repo.exists(
                grant_type="refresh_token", grant_data=refresh_token
            )
            is True
        )

    @pytest.mark.asyncio
    async def test_code_authorization_wrong_client_id(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)

        await self.persistent_grant_repo.create(
            client_id="double_test",
            grant_data="secret_code",
            user_id=2,
            grant_type="authorization_code",
            expiration_time=time.time() + 3600,
        )
        await connection.commit()
        wrong_params = {
            "client_id": "wrong_id",
            "grant_type": "authorization_code",
            "code": "secret_code",
            "scope": "test",
            "redirect_uri": "http://127.0.0.1:8888/callback/",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=wrong_params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "invalid_client",
        }

    @pytest.mark.asyncio
    async def test_code_authorization_without_redirect_uri(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)

        await self.persistent_grant_repo.create(
            client_id="double_test",
            grant_data="secret_code",
            user_id=2,
            grant_type="authorization_code",
            expiration_time=3600,
        )
        await connection.commit()

        wrong_params = {
            "client_id": "double_test",
            "grant_type": "authorization_code",
            "code": "secret_code",
            "scope": "test",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=wrong_params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "invalid_grant"
        }

    @pytest.mark.asyncio
    async def test_code_authorization_without_code(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)

        await self.persistent_grant_repo.create(
            client_id="double_test",
            grant_data="secret_code",
            user_id=2,
            grant_type="authorization_code",
            expiration_time=3600,
        )

        wrong_params = {
            "client_id": "double_test",
            "grant_type": "authorization_code",
            "scope": "test",
            "redirect_uri": "https://www.arnold-mann.net/",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=wrong_params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "invalid_grant"
        }

    @pytest.mark.asyncio
    async def test_code_authorization_client_without_grants(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)

        await self.persistent_grant_repo.create(
            client_id="double_test",
            grant_data="secret_code",
            user_id=2,
            grant_type="authorization_code",
            expiration_time=time.time() + 3600,
        )
        await self.persistent_grant_repo.create(
            client_id="test_client",
            grant_data="different_secret_code",
            user_id=1,
            grant_type="authorization_code",
            expiration_time=time.time() + 3600,
        )

        await connection.commit()

        wrong_params = {
            "client_id": "test_client",
            "grant_type": "authorization_code",
            "code": "secret_code",
            "scope": "test",
            "redirect_uri": "http://127.0.0.1:8888/callback/",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=wrong_params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "invalid_grant"
        }

    @pytest.mark.asyncio
    async def test_code_authorization_incorrect_code(
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "test_client",
            "grant_type": "authorization_code",
            "code": "incorrect_code",
            "scope": "test",
            "redirect_uri": "https://www.arnold-mann.net/",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "invalid_grant"
        }

    @pytest.mark.asyncio
    async def test_refresh_token_authorization(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        """
        It can pass only if the test above (test_code_authorization) passed.
        It uses refresh_token grant from that previous test.
        You can also just paste 'data' row from db that have proper client_id (double_test) and grant_type (refresh_token)
        to 'refresh_token' in params
        """

        test_token = await self.jwt_service.encode_jwt(
            payload={"sub": 1, "exp": time.time() + 3600}
        )

        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id="test_client",
            grant_data=test_token,
            user_id=1,
            grant_type="refresh_token",
            expiration_time=time.time() + 3600,
            scope='openid'
        )
        await connection.commit()
        params = {
            "client_id": "test_client",
            "grant_type": "refresh_token",
            "refresh_token": test_token,
            "scope": "openid",
            "redirect_uri": "https://www.arnold-mann.net/",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        response_json = response.json()
        print(response_json)
        data = response_json["refresh_token"]
        assert (
            await persistent_grant_repo.exists(
                grant_type="refresh_token", grant_data=data
            )
            is True
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_refresh_token_incorrect_token(
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "test_client",
            "grant_type": "refresh_token",
            "refresh_token": "incorrect_token",
            "scope": "test",
            "redirect_uri": "https://www.arnold-mann.net/",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "invalid_grant"
        }

    @pytest.mark.asyncio
    async def test_client_credentials_successful(
        self,
        client: AsyncClient,
    ) -> None:
        params = {
            "client_id": "test_client",
            "grant_type": "client_credentials",
            "client_secret": "past",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        response_content = json.loads(response.content.decode("utf-8"))
        assert response.status_code == status.HTTP_200_OK
        for param in (
            "access_token",
            "token_type",
            "expires_in",
            "not_before_policy",
            "scope",
        ):
            assert (
                response_content.get(param, "test not asserted")
                != "test not asserted"
            )

    @pytest.mark.asyncio
    async def test_client_credentials_incorrect_client_id(
        self,
        client: AsyncClient,
    ) -> None:
        params = {
            "client_id": "Star_Platinum",
            "grant_type": "client_credentials",
            "client_secret": "past",
        }
        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "invalid_client"
        }

    @pytest.mark.asyncio
    async def test_client_credentials_incorrect_client_secret(
        self,
        client: AsyncClient,
    ) -> None:
        params = {
            "client_id": "test_client",
            "grant_type": "client_credentials",
            "client_secret": "THE_WORLD",
        }
        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "invalid_client"
        }

    @pytest.mark.asyncio
    async def test_client_credentials_incorrect_scope(
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "test_client",
            "grant_type": "client_credentials",
            "client_secret": "past",
            "scope": "incorrect",
        }
        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "invalid_scope"
        }

    @pytest.mark.asyncio
    async def test_unsupported_grant_type(self, client: AsyncClient) -> None:
        params = {
            "client_id": "test_client",
            "grant_type": "unsupported",
            "scope": "test",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {
            "error": "unsupported_grant_type"
        }
