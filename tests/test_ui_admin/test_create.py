import json
import time

import pytest
import pytest_asyncio
from fastapi import status

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services import JWTService


class TestUIAdminLogin:
    content_type = "application/x-www-form-urlencoded"

    @pytest.mark.asyncio
    async def test_get_login(
            self, connection: AsyncSession,
            client: AsyncClient
    ):
        get_response = await client.get(
            "/admin/login"
        )
        assert get_response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_post_cookies_session_token(
            self, admin_credentials,
            connection: AsyncSession,
            client: AsyncClient
    ):
        auth_response = await client.post(
            "/admin/login",
            data=admin_credentials,
            headers={"Content-Type": self.content_type},
        )
        assert auth_response.status_code == status.HTTP_302_FOUND
        cookies = auth_response.cookies
        session_cookie = auth_response.cookies.get('session')
        assert cookies
        assert session_cookie


class TestUIAdminClient:

    @pytest.mark.asyncio
    async def test_get_client(self, admin_credentials, connection: AsyncSession, client: AsyncClient):

        get_response = await client.get(
            "/admin/login",
        )
        assert get_response.status_code == status.HTTP_200_OK


class TestUIAdminRead:
    content_type = "application/x-www-form-urlencoded"
    @pytest.mark.asyncio
    async def test_get_client(self, admin_credentials, connection: AsyncSession, client: AsyncClient):

        auth_response = await client.post(
            "/admin/login",
            data=admin_credentials,
            headers={"Content-Type": self.content_type},
        )
        assert auth_response.status_code == status.HTTP_302_FOUND
        cookies = auth_response.cookies
        session_cookie = auth_response.cookies.get('session')
        assert cookies
        assert session_cookie

        response = await client.get(
            "/admin/client/list",
            cookies={"session": session_cookie},
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_200_OK

class TestUIAdminCreate:
    jwt_service = JWTService()
    content_type = "application/x-www-form-urlencoded"

    @pytest.mark.asyncio
    async def test_create_client(
            self,
            client_create_data,
            connection: AsyncSession,
            client: AsyncClient,
            token: JWTService,
    ):
        response = await client.post(
            "/admin/client/create",
            data=client_create_data,
            headers={"Content-Type": self.content_type},
            cookies={"session": token},
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND

    @pytest.mark.asyncio
    async def test_create_device(
            self,
            device_create_data,
            connection: AsyncSession,
            client: AsyncClient,
            token: JWTService,
    ):
        response = await client.post(
            "/admin/client/create",
            data=device_create_data,
            headers={"Content-Type": self.content_type},
            cookies={"session": token},
        )
        await connection.flush()
        assert response.status_code == status.HTTP_302_FOUND




    # @pytest.mark.asyncio
    # async def test_create_device(
    #         self, device_create_data,
    #         admin_credentials,
    #         connection: AsyncSession,
    #         client: AsyncClient
    # ):
    #     auth_response = await client.post(
    #         "http://127.0.0.1:8000/admin/login",
    #         data=admin_credentials,
    #         headers={"Content-Type": self.content_type},
    #     )
    #     assert auth_response.status_code == status.HTTP_302_FOUND
    #     cookies = auth_response.cookies
    #     session_cookie = auth_response.cookies.get('session')
    #     assert cookies
    #     assert session_cookie
    #
    #     response = await client.post(
    #         "http://127.0.0.1:8000/admin/device/create",
    #         data=device_create_data,
    #         headers={"Content-Type": self.content_type},
    #         cookies=cookies,
    #     )
    #     # print(f"############### PRINT1 ########################")
    #     # print(response.text)
    #     assert response.status_code == 200

        # If the server returns the created device in the response, you can also check the returned data
        # created_device = response.json()
        #
        # assert created_device['client'] == device_data['client']
        # assert created_device['device_code'] == device_data['device_code']
        # assert created_device['user_code'] == device_data['user_code']