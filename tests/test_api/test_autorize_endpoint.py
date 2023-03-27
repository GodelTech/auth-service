import json
import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthorizeEndpointGET:
    async def test_successful_authorize_request(
        self, client: AsyncClient
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
        self, client: AsyncClient
    ) -> None:
        params = {
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_authorize_request_wrong_client(
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "wrong_test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert json.loads(response.content) == {
            "error": "invalid_client",
            "error_description": "Client authentication failed.",
        }

    async def test_unsuccessful_authorize_request_bad_uri(
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "local_scope",
            "redirect_uri": "just_uri",
        }
        expected_content = '{"error": "invalid_request","error_description": "The client redirect_uri could not be found in the database."}'
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert json.loads(response.content) == {
            "error": "invalid_request",
            "error_description": "The client redirect_uri could not be found in the database.",
        }

    async def test_unsuccessful_authorize_request_bad_response_type(
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "some_type",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


@pytest.mark.asyncio
class TestAuthorizeEndpointPOST:
    content_type = "application/x-www-form-urlencoded"

    async def test_successful_authorize_request(
        self, client: AsyncClient
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
        self, client: AsyncClient
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
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "wrong_test_client",
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

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert json.loads(response.content) == {
            "error": "invalid_client",
            "error_description": "Client authentication failed.",
        }

    async def test_unsuccessful_authorize_request_badpassword(
        self, client: AsyncClient
    ):
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
            "username": "TestClient",
            "password": "Wrong",
        }
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    async def test_unsuccessful_authorize_request_bad_username(
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
            "username": "WrongUsername",
            "password": "password",
        }
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
