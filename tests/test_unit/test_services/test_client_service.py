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

@pytest.mark.asyncio
class TestClientService:
    async def test_registration(self, client_service: ClientService) -> None:
       client_service.request_model = ClientRequestModel()
       result = await client_service.registration()
       assert "client_secret" in result.keys()
       assert "client_id" in result.keys()
       client = await client_service.client_repo.get_client_by_client_id(client_id=result["client_id"])
       assert client.client_name == "Example app"