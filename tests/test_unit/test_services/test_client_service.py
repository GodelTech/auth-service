import mock
import pytest
from sqlalchemy import delete

from src.business_logic.services import ClientService
from sqlalchemy.ext.asyncio.engine import AsyncEngine

class ClientRequestModel():
        client_name = "Example app"
        client_uri = "example_app.com"
        logo_uri = "example_app.com/pic.jpg"
        redirect_uris = ["example_app.com/redirect_uri_1" , "example_app.com/redirect_uri_2"]
        grant_types = ["authorization_code"]
        response_types = ["code"]
        token_endpoint_auth_method = "client_secret_post"
        scope = "openid profile"

class ClientRequestModel2():
        client_name = "Real app"
        client_uri = None
        logo_uri = None
        redirect_uris = ["realapp.com", "real__app.com/callback"]
        grant_types = None
        response_types = None
        token_endpoint_auth_method = None
        scope = "email"

@pytest.mark.asyncio
class TestClientService:
        async def test_registration_and_update(self, client_service: ClientService) -> None:
                client_service.request_model = ClientRequestModel()
                result = await client_service.registration()
                assert "client_secret" in result.keys()
                assert "client_id" in result.keys()
                client_id = result["client_id"]
                client = await client_service.client_repo.get_client_by_client_id(client_id=result["client_id"])
                assert client.client_name == "Example app"

                client_service.request_model = ClientRequestModel2()
                result = await client_service.update(client_id=client_id)
                client = await client_service.client_repo.get_client_by_client_id(client_id=client_id)
                assert client.client_name == "Real app"

        async def test_get_all(self, client_service: ClientService) -> None:
                client_service.request_model = ClientRequestModel()
                result = await client_service.get_all()
                assert result
                