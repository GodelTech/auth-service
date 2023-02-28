import pytest
from fastapi import status
from httpx import AsyncClient

scope = (
    "gcp-api%20IdentityServerApi&grant_type="
    "password&client_id=test_client&client_secret="
    "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
    "test_password&username=TestClient"
)


@pytest.mark.asyncio
class TestAuthorizeEndpoint:
    async def test_successful_authorize_request_get(self, client: AsyncClient) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_200_OK

    async def test_unsuccessful_authorize_request_not_full_data_get(
        self, client: AsyncClient
    ) -> None:
        params = {
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_authorize_request_wrong_client_get(
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "wrong_test_client",
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        expected_content = '{"message":"Client not found"}'
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_unsuccessful_authorize_request_bad_uri_get(
        self, client: AsyncClient
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
        self, client: AsyncClient
    ) -> None:
        local_scope = (
            "gcp-api%20IdentityServerApi&grant_type="
            "password&client_id=test_client&client_secret="
            "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
            # "wrong_password&username=BadNameTestClient"
        )
        params = {
            "client_id": "test_client",
            "response_type": "some_type",
            "scope": local_scope,
            "redirect_uri": "https://www.google.com/",
        }
        expected_content = '{"message":"Bad response type"}'
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.content.decode("UTF-8") == expected_content


@pytest.mark.asyncio
class TestAuthoriseEndpointPOST:
    content_type = "application/x-www-form-urlencoded"

    async def test_successful_authorize_request_post(self, client: AsyncClient) -> None:
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_302_FOUND

    async def test_unsuccessful_authorize_request_not_full_data_post(
        self, client: AsyncClient
    ) -> None:
        params = {
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_authorize_request_wrong_client_post(
        self, client: AsyncClient
    ) -> None:
        params = {
            "client_id": "wrong_test_client",
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
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

    async def test_unsuccessful_authorize_request_bad_password_post(
        self, client: AsyncClient
    ) -> None:
        local_scope = (
            "gcp-api%20IdentityServerApi&grant_type="
            "password&client_id=test_client&client_secret="
            "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
            "wrong_password&username=TestClient"
        )
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": local_scope,
            "redirect_uri": "https://www.google.com/",
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

    async def test_unsuccessful_authorize_request_bad_user_name_post(
        self, client: AsyncClient
    ) -> None:
        local_scope = (
            "gcp-api%20IdentityServerApi&grant_type="
            "password&client_id=test_client&client_secret="
            "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
            "wrong_password&username=BadNameTestClient"
        )
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": local_scope,
            "redirect_uri": "https://www.google.com/",
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

    async def test_unsuccessful_authorize_request_wrong_scope_key_error_post(
        self, client: AsyncClient
    ) -> None:
        local_scope = "gcp-api%20IdentityServerApi&grant_type=password&client_id=test_client"
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": local_scope,
            "redirect_uri": "https://www.google.com/",
        }
        expected_content = (
            '{"message":"The scope is missing a password, or a username"}'
        )
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": self.content_type},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
