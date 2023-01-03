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
class TestAuthoriseEndpoint:
    async def test_successful_authorize_request(self, client: AsyncClient):
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_302_FOUND

    async def test_unsuccessful_authorize_request_not_full_data(
        self, client: AsyncClient
    ):
        params = {
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_authorize_request_wrong_client(
        self, client: AsyncClient
    ):
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

    async def test_unsuccessful_authorize_request_bad_password(
        self, client: AsyncClient
    ):
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
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_unsuccessful_authorize_request_bad_user_name(
        self, client: AsyncClient
    ):
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
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_unsuccessful_authorize_request_wrong_scope_index_error(
        self, client: AsyncClient
    ):
        local_scope = "gcp-api%20IdentityServerApi&grant_type"
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": local_scope,
            "redirect_uri": "https://www.google.com/",
        }
        expected_content = '{"message":"Impossible to parse the scope"}'
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_unsuccessful_authorize_request_wrong_scope_key_error(
        self, client: AsyncClient
    ):
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
        response = await client.request("GET", "/authorize/", params=params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
