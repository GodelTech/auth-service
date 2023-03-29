import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, text, exists

from src.data_access.postgresql.tables.device import Device
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.business_logic.services.jwt_token import JWTService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine


TOKEN_HINT_DATA = {
    "sub": 1,
    "client_id": "test_client",
    "type": "urn:ietf:params:oauth:grant-type:device_code",
}


@pytest.mark.asyncio
class TestDeviceFlow:
    content_type = "application/x-www-form-urlencoded"

    async def test_successful_device_flow(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        # 1st stage Create a device instance the database for the relevant client
        params = {"client_id": "test_client", "scope": "openid"}
        response = await client.request(
            "POST",
            "/device/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_200_OK
        device = await connection.execute(
            select(exists().where(Device.client_id == 1))
        )
        device = device.first()
        assert device[0] is True

        # 2nd stage: Check request to Device Login form
        response = await client.request("GET", "/device/auth")

        assert response.status_code == status.HTTP_200_OK
        assert type(response.content) == bytes

        # 3rd stage: Check the user_code and make redirect to the authorization endpoint with GET
        device = await connection.execute(
            select(Device).where(Device.client_id == 1)
        )
        device = device.first()[0]
        user_code = device.user_code
        device_code = device.device_code
        param_3rd = {
            "user_code": user_code,
        }
        response = await client.request(
            "POST",
            "/device/auth",
            data=param_3rd,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_302_FOUND

        # 4th stage: authorization endpoint with GET
        params_4th = {
            "client_id": "test_client",
            "response_type": "urn:ietf:params:oauth:grant-type:device_code",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request(
            "GET", "/authorize/", params=params_4th
        )
        assert response.status_code == status.HTTP_200_OK

        # 5th stage: suppose we press confirm, this requests the redirect to authorization endpoint with POST
        scope_data = "openid" + f"&user_code={user_code}"
        params_5th = {
            "client_id": "test_client",
            "response_type": "urn:ietf:params:oauth:grant-type:device_code",
            "scope": scope_data,
            "redirect_uri": "https://www.google.com/",
            "username": "TestClient",
            "password": "test_password",
        }

        response = await client.request(
            "POST",
            "/authorize/",
            data=params_5th,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_302_FOUND
        device = await connection.execute(
            select(exists().where(Device.client_id == 1))
        )
        device = device.first()
        assert device[0] is False
        device = await connection.execute(
            select(exists().where(PersistentGrant.grant_data == device_code))
        )
        device = device.first()
        assert device[0] is True

        # 6th stage Token endpoint changes secrete code in Persistent grant table to token
        params_6th = {
            "client_id": "test_client",
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "scope": "test",
            "redirect_uri": "https://www.google.com/",
        }

        response = await client.request(
            "POST",
            "/token/",
            data=params_6th,
            headers={"Content-Type": self.content_type},
        )
        response_data = response.json()
        access_token = response_data.get("access_token")
        assert response.status_code == status.HTTP_200_OK

        # 7th stage UserInfo endpoint retrieves user data from UserClaims table

        # The sequence id number is out of sync and raises duplicate key error
        # We manually bring it back in sync
        await connection.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('user_claims', 'id'), (SELECT MAX(id) FROM user_claims)+1);"
            )
        )
        response = await client.request(
            "GET", "/userinfo/", headers={"authorization": access_token}
        )
        assert response.status_code == status.HTTP_200_OK

        # 8th stage EndSession endpoint deletes all records in the Persistent grant table for the corresponding user
        jwt_service = JWTService()

        id_token_hint = await jwt_service.encode_jwt(payload=TOKEN_HINT_DATA)

        params = {
            "id_token_hint": id_token_hint,
            "post_logout_redirect_uri": "http://thompson-chung.com/",
            "state": "test_state",
        }
        response = await client.request("GET", "/endsession/", params=params)
        assert response.status_code == status.HTTP_302_FOUND

        # 9th stage: check success form
        response = await client.request("GET", "/device/auth/success")

        assert response.status_code == status.HTTP_200_OK
        assert type(response.content) == bytes

    async def test_unsuccessful_device_flow(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        # 1st stage Create a device instance the database for the relevant client
        params = {
            "client_id": "test_client",
        }
        response = await client.request(
            "POST",
            "/device/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_200_OK
        device = await connection.execute(
            select(exists().where(Device.client_id == 1))
        )
        device = device.first()
        assert device[0] is True

        # 2nd stage: Check request to Device Login form
        response = await client.request("GET", "/device/auth")

        assert response.status_code == status.HTTP_200_OK
        assert type(response.content) == bytes

        # 3rd stage: Check the user_code and make redirect to the authorization endpoint with GET
        device = await connection.execute(
            select(Device).where(Device.client_id == 1)
        )
        device = device.first()[0]
        user_code = device.user_code
        param_3rd = {
            "user_code": user_code,
        }
        response = await client.request(
            "POST",
            "/device/auth",
            data=param_3rd,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_302_FOUND

        # 4th stage: authorization endpoint with GET
        params_4th = {
            "client_id": "test_client",
            "response_type": "urn:ietf:params:oauth:grant-type:device_code",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request(
            "GET", "/authorize/", params=params_4th
        )
        assert response.status_code == status.HTTP_200_OK

        # 5th stage: suppose we press cancel, then uoe code cleans the device table
        param_next = {
            "client_id": "test_client",
            "scope": f"user_code={user_code}",
        }
        response = await client.request(
            "DELETE",
            "/device/auth/cancel",
            data=param_next,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_200_OK
        device = await connection.execute(
            select(exists().where(Device.client_id == 1))
        )
        device = device.first()
        assert device[0] is False

        # 6th stage: check cancel form
        response = await client.request("GET", "/device/auth/cancel")

        assert response.status_code == status.HTTP_200_OK
        assert type(response.content) == bytes
