import pytest
from sqlalchemy import delete, insert, text

from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    UserNotFoundError,
    WrongPasswordError,
)
from src.data_access.postgresql.tables.client import Client
from tests.test_unit.fixtures import DEFAULT_CLIENT, authorization_request_model
from src.business_logic.services.authorization import AuthorizationService
from src.presentation.api.models.authorization import RequestModel
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from typing import Any


@pytest.mark.asyncio
class TestAuthorizationService:
    async def test_get_redirect_url_code(
        self, 
        authorization_service: AuthorizationService, 
        authorization_request_model: RequestModel
    ) -> None:
        service = authorization_service
        service.request_model = authorization_request_model
        expected_url = "https://www.google.com/"
        redirect_url = await service.get_redirect_url()
        if not redirect_url:
            raise AssertionError
        redirect_url = redirect_url.split("?")[0]

        assert expected_url == redirect_url

    async def test_get_redirect_url_token(
        self, 
        authorization_service: AuthorizationService,
        authorization_request_model: RequestModel
    ) -> None:
        authorization_request_model.response_type = "token"
        service = authorization_service
        service.request_model = authorization_request_model
        expected_url = "https://www.google.com/"
        redirect_url = await service.get_redirect_url()
        if not redirect_url:
            raise AssertionError
        data = {
            item.split("=")[0]: item.split("=")[1]
            for item in redirect_url.split("?")[1].split("&")
        }

        redirect_url = redirect_url.split("?")[0]
        assert expected_url == redirect_url
        assert "access_token" in data
        assert "id_token" not in data
        assert data["token_type"] in "Bearer"

    async def test_get_redirect_url_id_token_token(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        authorization_request_model.response_type = "id_token token"
        service = authorization_service
        service.request_model = authorization_request_model
        expected_url = "https://www.google.com/"
        redirect_url = await service.get_redirect_url()
        if not redirect_url:
            raise AssertionError
        data = {
            item.split("=")[0]: item.split("=")[1]
            for item in redirect_url.split("?")[1].split("&")
        }
        redirect_url = redirect_url.split("?")[0]
        assert expected_url == redirect_url
        assert "access_token" in data
        assert "id_token" in data
        assert data["token_type"] in "Bearer"

    async def test_get_redirect_url_wrong_client(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        service = authorization_service
        service.request_model = authorization_request_model
        service.request_model.client_id = "not_exist_client"
        with pytest.raises(ClientNotFoundError):
            await service.get_redirect_url()

    async def test_get_redirect_url_wrong_scope_key(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        service = authorization_service
        service.request_model = authorization_request_model
        service.request_model.scope = "gcp-api%20IdentityServerApi&grant_type=password&client_id=test_client"
        with pytest.raises(KeyError):
            await service.get_redirect_url()

    async def test_get_redirect_url_wrong_scope_no_password(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        service = authorization_service
        service.request_model = authorization_request_model
        service.request_model.scope = "gcp-api%20IdentityServerApi&grant_type"
        with pytest.raises(KeyError):
            await service.get_redirect_url()

    async def test_get_redirect_url_wrong_scope_password(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        service = authorization_service
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
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        service = authorization_service
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

    async def test_get_redirect_url_without_scope(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        service = authorization_service
        service.request_model = authorization_request_model
        service.request_model.scope = None
        result = await service.get_redirect_url()
        assert result is None

    async def test_get_redirect_url_id_without_request_model(
        self, authorization_service: AuthorizationService
    ) -> None:
        service = authorization_service
        result = await service.get_redirect_url()
        assert result is None

    async def test_validate_client(self, authorization_service: AuthorizationService, connection: AsyncEngine) -> None:
        # The sequence id number is out of sync and raises duplicate key error
        # We manually bring it back in sync
        await connection.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('clients', 'id'), (SELECT MAX(id) FROM clients)+1);"
            )
        )
        await connection.execute(insert(Client).values(**DEFAULT_CLIENT))
        await connection.commit()
        authorization_service.request_model = RequestModel(client_id='h', response_type='u', redirect_uri='y')
        client = await authorization_service._validate_client(
            client_id="default_test_client"
        )
        assert bool(client) is True
        await connection.execute(
            delete(Client).where(Client.client_id == "default_test_client")
        )
        await connection.commit()

    async def test_validate_client_error(self, authorization_service: AuthorizationService) -> None:
        with pytest.raises(ClientNotFoundError):
            authorization_service.request_model = RequestModel(client_id='h', response_type='u', redirect_uri='y')
            await authorization_service._validate_client(
                client_id="test_client_not_exist"
            )

    async def test_parse_scope_data(self, authorization_service: AuthorizationService) -> None:
        expected_password = "BestOfTheBest"
        expected_client_id = "tony_stark"
        expected_username = "IronMan"

        to_parse = "gcp-api%20IdentityServerApi&client_id=tony_stark&password=BestOfTheBest&username=IronMan"
        result = await authorization_service._parse_scope_data(to_parse)
        assert result["client_id"] == expected_client_id
        assert result["password"] == expected_password
        assert result["username"] == expected_username

    async def test_parse_scope_data_len_two(self, authorization_service: AuthorizationService) -> None:
        expected_password = "BestOfTheBest"
        expected_username = "IronMan"

        to_parse = "password=BestOfTheBest&username=IronMan"
        result = await authorization_service._parse_scope_data(to_parse)
        assert result["password"] == expected_password
        assert result["username"] == expected_username

    async def test_parse_empty_scope(self, authorization_service: AuthorizationService) -> None:
        expected:dict[str, Any] = {}
        to_parse = ""
        result = await authorization_service._parse_scope_data(to_parse)
        assert result == expected

    async def test_parse_scope_without_separator(self, authorization_service: AuthorizationService) -> None:
        expected = {'some_key': "key"}
        to_parse = "some_key=key"
        result = await authorization_service._parse_scope_data(to_parse)
        assert result == expected

    async def test_update_redirect_url_with_state(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        authorization_service.request_model = authorization_request_model
        expected_url = "https://www.google.com/?code=secret&state=state"
        redirect_url = (
            await authorization_service._update_redirect_url_with_params(
                "secret"
            )
        )

        assert redirect_url == expected_url

    async def test_update_redirect_url_without_request_model(
        self, authorization_service: AuthorizationService
    ) -> None:
        result = await authorization_service._update_redirect_url_with_params(
            "secret"
        )
        assert result is None

    async def test_update_redirect_url_without_state(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        authorization_service.request_model = authorization_request_model
        authorization_service.request_model.state = None
        expected_url = "https://www.google.com/?code=secret"
        redirect_url = (
            await authorization_service._update_redirect_url_with_params(
                "secret"
            )
        )

        assert redirect_url == expected_url

    async def test_get_redirect_url_code_response_type(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        expected_start = "https://www.google.com/"
        authorization_service.request_model = authorization_request_model
        result_uri = (
            await authorization_service.get_redirect_url_code_response_type(
                user_id=2
            )
        )
        if not result_uri:
            raise AssertionError
        if not result_uri:
            raise AssertionError
        start_uri = result_uri.split("?")[0]
        data = {
            item.split("=")[0]: item.split("=")[1]
            for item in result_uri.split("?")[1].split("&")
        }

        assert start_uri == expected_start
        assert data["state"] == "state"
        assert "access_token" not in data
        assert "code" in data

        await authorization_service.persistent_grant_repo.delete(
            grant_data=data["code"], grant_type="code"
        )

    async def test_get_redirect_url_code_response_type_without_request_model(
        self, authorization_service: AuthorizationService
    ) -> None:
        result = (
            await authorization_service.get_redirect_url_code_response_type(
                user_id=2
            )
        )
        assert result is None

    async def test_get_redirect_url_device_code_response_type_without_request_model(
        self, authorization_service: AuthorizationService
    ) -> None:
        result = await authorization_service.get_redirect_url_device_code_response_type(
            user_id=2
        )
        assert result is None

    async def test_get_redirect_url_token_response_type(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        expected_start = "https://www.google.com/"
        authorization_request_model.response_type = "token"
        authorization_service.request_model = authorization_request_model
        result_uri = (
            await authorization_service.get_redirect_url_token_response_type(
                user_id=2
            )
        )
        if not result_uri:
            raise AssertionError
        start_uri = result_uri.split("?")[0]
        data = {
            item.split("=")[0]: item.split("=")[1]
            for item in result_uri.split("?")[1].split("&")
        }
        assert start_uri == expected_start
        assert "access_token" in data
        assert "id_token" not in data
        assert data["token_type"] in "Bearer"

    async def test_get_redirect_url_token_response_type_without_request_model(
        self, authorization_service: AuthorizationService
    ) -> None:
        result = (
            await authorization_service.get_redirect_url_token_response_type(
                user_id=2
            )
        )
        assert result is None

    async def test_get_redirect_url_id_token_token_response_type(
        self, authorization_service: AuthorizationService, authorization_request_model: RequestModel
    ) -> None:
        expected_start = "https://www.google.com/"
        authorization_request_model.response_type = "id_token token"
        authorization_service.request_model = authorization_request_model
        result_uri = await authorization_service.get_redirect_url_id_token_token_response_type(
            user_id=2
        )
        if not result_uri:
            raise AssertionError
        start_uri = result_uri.split("?")[0]
        data = {
            item.split("=")[0]: item.split("=")[1]
            for item in result_uri.split("?")[1].split("&")
        }
        assert start_uri == expected_start
        assert "access_token" in data
        assert "id_token" in data
        assert data["token_type"] in "Bearer"

    async def test_get_redirect_url_id_token_token_response_type_without_request_model(
        self, authorization_service: AuthorizationService
    ) -> None:
        result = await authorization_service.get_redirect_url_id_token_token_response_type(
            user_id=2
        )
        assert result is None
