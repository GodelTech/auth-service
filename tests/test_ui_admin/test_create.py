import pytest
from fastapi import status
from sqlalchemy import insert
# from src.business_logic.dto import AdminCredentialsDTO
from src.data_access.postgresql.tables import User

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import base64
import json

from src.data_access.postgresql.tables.device import Device

@pytest.fixture
def device_data():
    return {
        'client': 'client_example',
        'device_code': 'device_code_example',
        'user_code': 'user_code_example'
    }

@pytest.fixture
def admin_credentials():
    return {
        'username': 'TestClient',
        'password': 'test_password'
    }

class TestUIAdminCreate:
    @pytest.mark.asyncio
    async def test_create_device(device_data, admin_credentials, connection: AsyncSession, client: AsyncClient):
        content_type = "application/x-www-form-urlencoded"
        # get_response = await client.get(
        #     "http://127.0.0.1:8000/admin/login"
        # )
        # assert get_response.status_code == 200

        auth_response = await client.post(
            "http://127.0.0.1:8000/admin/login",
            data=admin_credentials,
            headers={"Content-Type": content_type},
        )
        assert auth_response.status_code == status.HTTP_302_FOUND
        # print()
        # print(f"############################# PRINT1 #####################################")
        # print(auth_response)
        # print(auth_response.content)
        # print(f"############################# PRINT2 #####################################")
        cookies = auth_response.cookies
        # print(cookies)
        session_cookie = auth_response.cookies.get('session')
        # print(f"############################# PRINT3 #####################################")
        # print(f"session_cookie: {session_cookie}")
        assert cookies
        assert "session" in cookies
        # assert False

        response = await client.get("http://127.0.0.1:8000/admin/client/list", cookies=cookies)
        # response = await client.post("http://127.0.0.1:8000/admin/device/create",
        #                          data=device_data, cookies=cookies)

        assert response.status_code == 200

        # If the server returns the created device in the response, you can also check the returned data
        # created_device = response.json()
        #
        # assert created_device['client'] == device_data['client']
        # assert created_device['device_code'] == device_data['device_code']
        # assert created_device['user_code'] == device_data['user_code']