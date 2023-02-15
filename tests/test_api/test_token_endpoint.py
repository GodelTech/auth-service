import json
import time

import pytest
from fastapi import status
from httpx import AsyncClient, Client

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)


@pytest.mark.asyncio
class TestTokenEndpoint:
    jwt_service = JWTService()
    refresh_token = None
    content_type = 'application/x-www-form-urlencoded'

    @pytest.mark.asyncio
    async def test_code_authorization(
        self, client: AsyncClient, engine, token_service
    ):
        self.persistent_grant_repo = PersistentGrantRepository(engine)
        service = token_service
        await service.persistent_grant_repo.create(
            client_id='double_test',
            grant_data='secret_code',
            user_id=1,
            grant_type='code',
            expiration_time=3600,
        )

        params = {
            'client_id': 'double_test',
            'grant_type': 'code',
            'code': 'secret_code',
            'scope': 'test',
            'redirect_uri': 'https://www.arnold-mann.net/',
        }

        response = await client.request(
            'POST',
            '/token/',
            data=params,
            headers={'Content-Type': self.content_type},
        )

        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        pytest.refresh_token = response_json['refresh_token']
        assert (
            await service.persistent_grant_repo.exists(
                grant_type='refresh_token', data=pytest.refresh_token
            )
            is True
        )

    @pytest.mark.asyncio
    async def test_refresh_token_authorization(
        self, client: AsyncClient, engine
    ):
        '''
        It can pass only if the test above (test_code_authorization) passed.
        It uses refresh_token grant from that previous test.
        You can also just paste 'data' row from db that have proper client_id (double_test) and grant_type (refresh_token)
        to 'refresh_token' in params
        '''

        test_token = await self.jwt_service.encode_jwt(
            payload={'sub': 1, 'exp': time.time() + 3600}
        )

        persistent_grant_repo = PersistentGrantRepository(engine)
        await persistent_grant_repo.create(
            client_id='test_client',
            grant_data=test_token,
            user_id=1,
            grant_type='refresh_token',
        )

        params = {
            'client_id': 'double_test',
            'grant_type': 'refresh_token',
            'refresh_token': test_token,
            'scope': 'test',
            'redirect_uri': 'https://www.arnold-mann.net/',
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={'Content-Type': self.content_type},
        )
        response_json = response.json()
        data = response_json['refresh_token']
        assert (
            await persistent_grant_repo.exists(
                grant_type='refresh_token', data=data
            )
            is True
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_wrong_client_id(self, client: AsyncClient, engine):
        self.persistent_grant_repo = PersistentGrantRepository(engine)

        await self.persistent_grant_repo.create(
            client_id='double_test',
            grant_data='secret_code',
            user_id=2,
            grant_type='code',
            expiration_time=3600,
        )

        wrong_params = {
            'client_id': 'wrong_id',
            'grant_type': 'code',
            'code': 'secret_code',
            'scope': 'test',
            'redirect_uri': 'https://www.arnold-mann.net/',
        }

        response = await client.request(
            'POST',
            '/token/',
            data=wrong_params,
            headers={'Content-Type': self.content_type},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_code_authorization_incorrect_code(
        self, client: AsyncClient
    ):
        params = {
            'client_id': 'test_client',
            'grant_type': 'code',
            'code': 'incorrect_code',
            'scope': 'test',
            'redirect_uri': 'https://www.arnold-mann.net/',
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={'Content-Type': self.content_type},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_refresh_token_incorrect_token(self, client: AsyncClient):
        params = {
            'client_id': 'test_client',
            'grant_type': 'refresh_token',
            'refresh_token': 'incorrect_token',
            'scope': 'test',
            'redirect_uri': 'https://www.arnold-mann.net/',
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={'Content-Type': self.content_type},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_client_credentials_successful(
        self, client: AsyncClient, connection
    ):

        params = {
            'client_id': 'test_client',
            'grant_type': 'client_credentials',
            'client_secret': 'past',
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={'Content-Type': self.content_type},
        )
        response_content = json.loads(response.content.decode('utf-8'))
        assert response.status_code == status.HTTP_200_OK
        for param in (
            "access_token",
            "token_type",
            "expires_in",
            "refresh_expires_in",
            "not_before_policy",
            "scope",
        ):
            assert (
                response_content.get(param, 'test not asserted')
                != 'test not asserted'
            )

    @pytest.mark.asyncio
    async def test_client_credentials_incorrect_client_id(
        self, client: AsyncClient, connection
    ):

        params = {
            'client_id': 'Star_Platinum',
            'grant_type': 'client_credentials',
            'client_secret': 'past',
        }
        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={'Content-Type': self.content_type},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_client_credentials_incorrect_client_secret(
        self, client: AsyncClient, connection
    ):

        params = {
            'client_id': 'test_client',
            'grant_type': 'client_credentials',
            'client_secret': 'THE_WORLD',
        }
        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={'Content-Type': self.content_type},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
