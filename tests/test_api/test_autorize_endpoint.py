import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.asyncio
class TestAuthorizeEndpointGET:
    async def test_successful_authorize_request(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_200_OK

    async def test_unsuccessful_authorize_request_not_full_data(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        params = {
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_authorize_request_wrong_client(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        params = {
            "client_id": "wrong_test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        expected_content = '{"message":"Client not found"}'
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_unsuccessful_authorize_request_bad_uri(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "local_scope",
            "redirect_uri": "just_uri",
        }
        expected_content = '{"message":"Redirect Uri not found"}'
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_unsuccessful_authorize_request_bad_response_type(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "some_type",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        expected_content = '{"message":"Bad response type"}'
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.content.decode("UTF-8") == expected_content


@pytest.mark.asyncio
class TestAuthorizeEndpointPOST:
    content_type = "application/x-www-form-urlencoded"

    async def test_successful_authorize_request(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
            "username": "TestClient",
            "password": "test_password",
        }
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_302_FOUND

    async def test_unsuccessful_authorize_request_not_full_data(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        params = {
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_authorize_request_wrong_client(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        params = {
            "client_id": "wrong_test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
            "username": "TestClient",
            "password": "test_password",
        }
        expected_content = '{"message":"Client not found"}'
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_unsuccessful_authorize_request_badpassword(
        self, client: AsyncClient, engine: AsyncEngine,
    ):
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
            "username": "TestClient",
            "password": "Wrong",
        }
        expected_content = '{"message":"Bad password"}'
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_unsuccessful_authorize_request_bad_username(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
            "username": "WrongUsername",
            "password": "password",
        }
        expected_content = '{"message":"User not found"}'
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
