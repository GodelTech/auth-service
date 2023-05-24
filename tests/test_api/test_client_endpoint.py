import uuid

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import sessionmaker

from src.business_logic.services import JWTService
from src.data_access.postgresql.repositories import ClientRepository
from src.data_access.postgresql.tables.client import Client


@pytest.mark.asyncio
class TestClientEndpointPOST:
    content_type = "application/x-www-form-urlencoded"
    async def test_successful_registration_request(
        self, client: AsyncClient, engine: AsyncEngine
    ) -> None:

        request_body = {
            "redirect_uris": ["https://example.com/callback"],
            "client_name": "Test Client Registration",
            "client_uri": "https://example.com",
            "logo_uri": "https://example.com/logo.png",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid email"
        }

        response = await client.request("POST",
                                        "/clients/register",
                                        data=request_body,
                                        headers={"Content-Type": self.content_type})

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json()["client_id"], str)
        assert isinstance(response.json()["client_secret"], str)


    async def test_unsuccessful_registration_request_absence_required_redirect_uris(
            self, client: AsyncClient, engine: AsyncEngine
    ) -> None:
        request_body = {
            "redirect_uris": [],
            "client_name": "Test Client Registration",
            "client_uri": "https://example.com",
            "logo_uri": "https://example.com/logo.png",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid email"
        }

        response = await client.request("POST",
                                        "/clients/register",
                                        data=request_body,
                                        headers={"Content-Type": self.content_type})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "client_id" not in response.json()
        assert "client_secret" not in response.json()


@pytest.mark.asyncio
class TestClientEndpointPUT:
    content_type = "application/x-www-form-urlencoded"

    @pytest.mark.asyncio
    async def test_successful_client_update(self, client: AsyncClient) -> None:
        request_body = {
            "client_name": "Test Client Registration",
        }

        response = await client.request("PUT", "clients/test_client", data=request_body)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Client data updated successfully"}

    @pytest.mark.asyncio
    async def test_unsuccessful_update_non_existent_client_id(self, client: AsyncClient) -> None:
        client_id = "non_existent_client"
        request_body = {
            "redirect_uris": ["https://example.com/callback"],
            "client_name": "Updated Client",
            "client_uri": "https://updated-example.com",
            "logo_uri": "https://updated-example.com/logo.png",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid email"
        }

        response = await client.request("PUT", "clients/non_existent_client", data=request_body)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestClientAllEndpointGET:
    @pytest.mark.asyncio
    async def test_successful_get_all_clients(self, client: AsyncClient) -> None:
        self.access_token = await JWTService().encode_jwt(
            payload={
                "stand": "CrazyDiamond",
                "aud": ["admin"]
            }
        )
        response = await client.request("GET", "clients", headers={
                                                        "access-token": self.access_token,
                                                        "Content-Type": "application/x-www-form-urlencoded",
                                                    })

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json()["all_clients"], list)
        assert all(isinstance(client, dict) for client in response.json()["all_clients"])

    @pytest.mark.asyncio
    async def test_unsuccessful_get_all_clients_missing_access_token(self, client: AsyncClient) -> None:

        response = await client.request("GET", "clients")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_unsuccessful_get_all_clients_wrong_access_token(self, client: AsyncClient) -> None:
        response = await client.request("GET", "clients", headers={"access_token": "wrong_access_token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
class TestClientEndpointGET:

    async def test_successful_client_get(
        self, client: AsyncClient
    ) -> None:
        response = await client.request("GET", "/clients/test_client")
        assert response.status_code == status.HTTP_200_OK

    async def test_unsuccessful_client_get_with_non_existent_client_id(
        self, client: AsyncClient
    ) -> None:
        response = await client.request("GET", "/clients/invalid_test_client")
        assert response.status_code == status.HTTP_404_NOT_FOUND



########## ????????? ##############
    # async def test_update_with_invalid_redirect_uris(self, client: AsyncClient) -> None:
    #
    #     request_body = {
    #         "redirect_uris": [],
    #     }
    #     response = await client.put("clients/test_client", data=request_body)
    #
    #     assert response.status_code == status.HTTP_404_NOT_FOUND
#
@pytest.mark.asyncio
class TestClientEndpointDELETE:
    @pytest.mark.asyncio
    async def test_successful_client_deletion(self, client: AsyncClient,
                                              engine: AsyncEngine) -> None:

        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2,
            "refresh_token_expiration_type_id": 1,
            "access_token_type_id": 1,
            "protocol_type_id": 1,
        }

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            await session.execute(insert(Client).values(**new_client))
            await session.commit()

        async with session_factory() as session:
            new_client = await session.execute(
                select(Client).where(Client.client_id == unique_client_id)
            )
            new_client = new_client.scalar_one_or_none()

        assert new_client is not None

        response = await client.request("DELETE", f"clients/{unique_client_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Client deleted successfully"}

    @pytest.mark.asyncio
    async def test_unsuccessful_client_deletion_non_existent_client_id(self, client: AsyncClient) -> None:

        response = await client.request("DELETE", "clients/non_existent_client_id")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"message": "Client not found"}