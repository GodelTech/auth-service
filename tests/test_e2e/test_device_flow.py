import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables import User, UserClaim
from src.data_access.postgresql.tables.device import Device

TOKEN_HINT_DATA = {
    "sub": None,
    "client_id": "test_client",
    "type": "urn:ietf:params:oauth:grant-type:device_code",
}


@pytest.mark.asyncio
class TestDeviceFlow:
    content_type = "application/x-www-form-urlencoded"

    async def test_successful_device_flow(self, client: AsyncClient, connection: AsyncSession) -> None:
        # Stage 1: Client requests a device code
        request_params = {"client_id": "test_client", "scope": "openid"}
        response = await client.request("POST", "/device/", data=request_params,
                                        headers={"Content-Type": self.content_type})
        response_data = response.json()
        device_code = response_data.get("device_code")
        user_code = response_data.get("user_code")
        assert response.status_code == status.HTTP_200_OK
        assert device_code is not None
        assert user_code is not None

        # Stage 2: User navigates to the device login form and checks the user_code
        response = await client.request("GET", "/device/auth")
        assert response.status_code == status.HTTP_200_OK

        response = await client.request("POST", "/device/auth", data={"user_code": user_code},
                                        headers={"Content-Type": self.content_type})
        assert response.status_code == status.HTTP_302_FOUND

        # Stage 3: Client requests user authorization (usually done by redirecting the user to an authorization form)
        auth_params = {"client_id": "test_client", "response_type": "urn:ietf:params:oauth:grant-type:device_code",
                       "redirect_uri": "https://www.google.com/"}
        response = await client.request("GET", "/authorize/", params=auth_params)
        assert response.status_code == status.HTTP_200_OK

        # Stage 4: User authorizes the client
        # In a real scenario, this would be done manually by the user in a web browser.
        # This is just a test, so we're simulating this step by making a request with the user's credentials.
        auth_params = {
            "client_id": "test_client",
            "response_type": "urn:ietf:params:oauth:grant-type:device_code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
            "username": "TestClient",
            "password": "test_password",
        }
        response = await client.request("POST", "/authorize/",
                                        data=auth_params,
                                        headers={"Content-Type": self.content_type},
                                        cookies={"user_code": user_code})
        assert response.status_code == status.HTTP_302_FOUND

        # Stage 5: Client exchanges the device code for an access token
        token_params = {"client_id": "test_client", "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "device_code": device_code, "redirect_uri": "https://www.google.com/"}
        response = await client.request("POST", "/token/", data=token_params,
                                        headers={"Content-Type": self.content_type})
        assert response.status_code == status.HTTP_200_OK

        # Verify that the client received an access token
        access_token = response.json().get("access_token")
        assert access_token is not None

        # Stage 6: Client uses the access token to access the user's resources
        user_id_query = select(User.id).where(User.username == "TestClient")
        user_id = (await connection.execute(user_id_query)).scalar_one_or_none()

        user_claim_insertion = insert(UserClaim).values(user_id=user_id, claim_type_id=1, claim_value="TEST_CLAIM")
        await connection.execute(user_claim_insertion)
        await connection.commit()

        response = await client.request("GET", "/userinfo/", headers={"authorization": access_token})
        assert response.status_code == status.HTTP_200_OK

        # Stage 7: User ends the session
        jwt_service = JWTService()
        TOKEN_HINT_DATA["sub"] = user_id
        id_token_hint = await jwt_service.encode_jwt(payload=TOKEN_HINT_DATA)
        end_session_params = {"id_token_hint": id_token_hint, "post_logout_redirect_uri": "http://thompson-chung.com/",
                              "state": "test_state"}
        response = await client.request("GET", "/endsession/", params=end_session_params)
        assert response.status_code == status.HTTP_302_FOUND

        # Verify that the session has ended
        response = await client.request("GET", "/device/auth/success")
        assert response.status_code == status.HTTP_200_OK

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
