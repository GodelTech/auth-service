import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, exists, delete

from src.data_access.postgresql.tables.device import Device


@pytest.mark.asyncio
class TestDeviceEndpoint:

    content_type = 'application/x-www-form-urlencoded'

    async def test_successful_post_device_authorize(self, client: AsyncClient, connection):
        params = {
            "client_id": "test_client",
            "scope": "scope"
        }
        response = await client.request("POST", "/device/", data=params, headers={'Content-Type': self.content_type})
        assert response.status_code == status.HTTP_200_OK
        device = await connection.execute(
            select(exists().where(Device.client_id == "test_client"))
        )
        device = device.first()
        assert device[0] is True
        await connection.execute(
            delete(Device).where(Device.client_id == "test_client")
        )
        await connection.commit()

    async def test_unsuccessful_post_device_authorize(self, client: AsyncClient):
        expected_content = '{"message":"Client not found"}'
        params = {
            "client_id": "client_not_exists_1245",
            "scope": "scope"
        }
        response = await client.request("POST", "/device/", data=params, headers={'Content-Type': self.content_type})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_get_device_user_code(self, client: AsyncClient):
        response = await client.request("GET", "/device/auth")

        assert response.status_code == status.HTTP_200_OK
        assert type(response.content) == bytes

    async def test_successful_post_device_user_code(self, client: AsyncClient, connection):
        params = {
            "client_id": "test_client",
            "scope": "scope"
        }
        response = await client.request("POST", "/device/", data=params, headers={'Content-Type': self.content_type})
        assert response.status_code == status.HTTP_200_OK
        device = await connection.execute(
            select(Device).where(Device.client_id == "test_client")
        )
        device = device.first()[0]
        user_code = device.user_code
        param_next = {"user_code": user_code}
        response = await client.request(
            "POST", "/device/auth", data=param_next, headers={'Content-Type': self.content_type}
        )

        assert response.status_code == status.HTTP_302_FOUND
        await connection.execute(
            delete(Device).where(Device.client_id == "test_client")
        )
        await connection.commit()

    async def test_unsuccessful_post_device_user_code(self, client: AsyncClient):
        expected_content = '{"message":"Wrong user code"}'

        param_next = {"user_code": "user_code_not_exists_1245"}
        response = await client.request(
            "POST", "/device/auth", data=param_next, headers={'Content-Type': self.content_type}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_get_device_login_confirm(self, client: AsyncClient):
        response = await client.request("GET", "/device/auth/success")

        assert response.status_code == status.HTTP_200_OK
        assert type(response.content) == bytes

    async def test_successful_post_device_cancel(self, client: AsyncClient, connection):
        params = {
            "client_id": "test_client",
            "scope": "scope"
        }
        response = await client.request("POST", "/device/", data=params, headers={'Content-Type': self.content_type})
        assert response.status_code == status.HTTP_200_OK

        device = await connection.execute(
            select(exists().where(Device.client_id == "test_client"))
        )
        device = device.first()
        assert device[0] is True

        device = await connection.execute(
            select(Device).where(Device.client_id == "test_client")
        )
        device = device.first()[0]
        user_code = device.user_code
        param_next = {
            "client_id": "test_client",
            "scope": f"user_code={user_code}",
        }
        response = await client.request(
            "DELETE", "/device/auth/cancel", data=param_next, headers={'Content-Type': self.content_type}
        )

        assert response.status_code == status.HTTP_200_OK
        device = await connection.execute(
            select(exists().where(Device.client_id == "test_client"))
        )
        device = device.first()
        assert device[0] is False

    async def test_unsuccessful_post_device_cancel_bad_user_code(self, client: AsyncClient):
        expected_content = '{"message":"Wrong user code"}'

        param = {
            "client_id": "test_client",
            "scope": "user_code=user_code_not_exists_1245",
        }
        response = await client.request(
            "DELETE", "/device/auth/cancel", data=param, headers={'Content-Type': self.content_type}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_unsuccessful_post_device_cancel_bad_client(self, client: AsyncClient):
        expected_content = '{"message":"Client not found"}'

        param = {
            "client_id": "client_not_exists_1245",
            "scope": "user_code=user_code_not_exists_1245",
        }
        response = await client.request(
            "DELETE", "/device/auth/cancel", data=param, headers={'Content-Type': self.content_type}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_get_device_cancel(self, client: AsyncClient):
        response = await client.request("GET", "/device/auth/cancel")

        assert response.status_code == status.HTTP_200_OK
        assert type(response.content) == bytes
