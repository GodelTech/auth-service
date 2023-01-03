import pytest
from sqlalchemy import insert

from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    UserNotFoundError,
    WrongPasswordError,
)
from src.data_access.postgresql.tables.client import Client
from tests.test_unit.fixtures import DEFAULT_CLIENT, authorization_request_model


@pytest.mark.asyncio
class TestAuthorisationService:
    async def test_get_redirect_url(
        self, authorisation_service, authorization_request_model
    ):
        service = authorisation_service
        service.request_model = authorization_request_model
        expected_url = "https://www.google.com/"
        redirect_url = await service.get_redirect_url()
        redirect_url = redirect_url.split("?")[0]

        assert expected_url == redirect_url

    async def test_get_redirect_url_wrong_client(
        self, authorisation_service, authorization_request_model
    ):
        service = authorisation_service
        service.request_model = authorization_request_model
        service.request_model.client_id = "not_exist_client"
        with pytest.raises(ClientNotFoundError):
            await service.get_redirect_url()

    async def test_get_redirect_url_wrong_scope_key(
        self, authorisation_service, authorization_request_model
    ):
        service = authorisation_service
        service.request_model = authorization_request_model
        service.request_model.scope = "gcp-api%20IdentityServerApi&grant_type=password&client_id=test_client"
        with pytest.raises(KeyError):
            await service.get_redirect_url()

    async def test_get_redirect_url_wrong_scope_index(
        self, authorisation_service, authorization_request_model
    ):
        service = authorisation_service
        service.request_model = authorization_request_model
        service.request_model.scope = "gcp-api%20IdentityServerApi&grant_type"
        with pytest.raises(IndexError):
            await service.get_redirect_url()

    async def test_get_redirect_url_wrong_scope_password(
        self, authorisation_service, authorization_request_model
    ):
        service = authorisation_service
        service.request_model = authorization_request_model
        scope = (
            "gcp-api%20IdentityServerApi&grant_type="
            "password&client_id=test_client&client_secret="
            "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
            "wrong_password&username=TestClient"
        )
        service.request_model.scope = scope
        with pytest.raises(WrongPasswordError):
            await service.get_redirect_url()

    async def test_get_redirect_url_wrong_scope_user_name(
        self, authorisation_service, authorization_request_model
    ):
        service = authorisation_service
        service.request_model = authorization_request_model
        scope = (
            "gcp-api%20IdentityServerApi&grant_type="
            "password&client_id=test_client&client_secret="
            "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
            "wrong_password&username=NotExistUser"
        )
        service.request_model.scope = scope
        with pytest.raises(UserNotFoundError):
            await service.get_redirect_url()

    async def test_validate_client(self, authorisation_service):
        await authorisation_service.client_repo.session.execute(
            insert(Client).values(**DEFAULT_CLIENT)
        )
        client = await authorisation_service._validate_client(
            client_id="default_test_client"
        )
        assert client is True

    async def test_validate_client_error(self, authorisation_service):
        with pytest.raises(ClientNotFoundError):
            await authorisation_service._validate_client(
                client_id="test_client_not_exist"
            )

    async def test_parse_scope_data(self, authorisation_service):
        expected_password = "BestOfTheBest"
        expected_client_id = "tony_stark"
        expected_username = "IronMan"

        to_parse = "gcp-api%20IdentityServerApi&client_id=tony_stark&password=BestOfTheBest&username=IronMan"
        result = await authorisation_service._parse_scope_data(to_parse)
        assert result["client_id"] == expected_client_id
        assert result["password"] == expected_password
        assert result["username"] == expected_username

    async def test_parse_empty_scope(self, authorisation_service):
        expected = {}
        to_parse = ""
        result = await authorisation_service._parse_scope_data(to_parse)
        assert result == expected

    async def test_parse_scope_without_separator(self, authorisation_service):
        expected = {}
        to_parse = "gcp-api%20IdentityServerApi=kjuhtgbmj"
        result = await authorisation_service._parse_scope_data(to_parse)
        assert result == expected

    async def test_parse_scope_data_index_error(self, authorisation_service):
        to_parse = "gcp-api%20IdentityServerApi&client_id"
        with pytest.raises(IndexError):
            await authorisation_service._parse_scope_data(to_parse)

    async def test_update_redirect_url_with_state(
        self, authorisation_service, authorization_request_model
    ):
        authorisation_service.request_model = authorization_request_model
        expected_url = "https://www.google.com/?code=secret&state=state"
        redirect_url = (
            await authorisation_service._update_redirect_url_with_params(
                "secret"
            )
        )

        assert redirect_url == expected_url

    async def test_update_redirect_url_without_state(
        self, authorisation_service, authorization_request_model
    ):
        authorisation_service.request_model = authorization_request_model
        authorisation_service.request_model.state = None
        expected_url = "https://www.google.com/?code=secret"
        redirect_url = (
            await authorisation_service._update_redirect_url_with_params(
                "secret"
            )
        )

        assert redirect_url == expected_url
