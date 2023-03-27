from tokenize import Token
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from sqlalchemy import delete, insert, text
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from src.business_logic.services.authorization.authorization_service import (
    AuthorizationService,
)
from src.business_logic.services.authorization.response_type_handlers import (
    TokenResponseTypeHandler,
    IdTokenResponseType,
    IdTokenTokenResponseTypeHandler,
    DeviceCodeResponseTypeHandler,
)
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientScopesError,
)
from src.data_access.postgresql.tables.client import Client
from src.presentation.api.models.authorization import DataRequestModel
from tests.test_unit.fixtures import (  # TODO shouldn't it be just in conftest files?
    DEFAULT_CLIENT,
    auth_post_request_model,
)

# TODO move it somewhere else


@pytest.fixture
def client_repository_mock():
    client_repo = AsyncMock()
    client_repo.validate_client_redirect_uri.return_value = None
    # Create a mock object for the client with an 'id' attribute
    mock_client = MagicMock()
    mock_client.id = 1
    client_repo.get_client_by_client_id.return_value = mock_client
    client_repo.get_client_scopes.return_value = "openid"
    yield client_repo
    del client_repo


@pytest.fixture
def user_repository_mock():
    user_repo = AsyncMock()
    user_repo.get_hash_password.return_value = (
        "hashed_password",
        1,
    )
    yield user_repo
    del user_repo


@pytest.fixture
def persistent_grant_repository_mock():
    return AsyncMock()


@pytest.fixture
def device_repository_mock():
    return AsyncMock()


@pytest.fixture
def password_hash_mock():
    return Mock()


@pytest.fixture
def jwt_service_mock():
    return AsyncMock()


@pytest.fixture
def auth_service_with_mocked_dependencies(
    client_repository_mock,
    user_repository_mock,
    persistent_grant_repository_mock,
    device_repository_mock,
    password_hash_mock,
    jwt_service_mock,
):
    auth_service = AuthorizationService(
        client_repo=client_repository_mock,
        user_repo=user_repository_mock,
        persistent_grant_repo=persistent_grant_repository_mock,
        device_repo=device_repository_mock,
        password_service=password_hash_mock,
        jwt_service=jwt_service_mock,
    )
    yield auth_service
    del auth_service


@pytest.fixture
def token_response_type_handler(
    auth_service_with_mocked_dependencies, auth_post_request_model
):
    auth_service_with_mocked_dependencies.request_model = (
        auth_post_request_model
    )
    handler = TokenResponseTypeHandler(auth_service_with_mocked_dependencies)
    yield handler
    del handler


@pytest.fixture
def id_token_response_type_handler(
    auth_service_with_mocked_dependencies, auth_post_request_model
):
    auth_service_with_mocked_dependencies.request_model = (
        auth_post_request_model
    )
    handler = IdTokenResponseType(auth_service_with_mocked_dependencies)
    yield handler
    del handler


@pytest.mark.asyncio
class TestAuthorizationService:
    async def test_request_model_not_provided(
        self, auth_service_with_mocked_dependencies
    ):
        with pytest.raises(ValueError):
            await auth_service_with_mocked_dependencies.request_model

    async def test_validate_scope(
        self, auth_service_with_mocked_dependencies, auth_post_request_model
    ):
        auth_service_with_mocked_dependencies.request_model = (
            auth_post_request_model
        )
        await auth_service_with_mocked_dependencies._validate_scope()

    async def test_validate_scope_with_incorrect_scope(
        self, auth_service_with_mocked_dependencies, auth_post_request_model
    ):
        auth_service_with_mocked_dependencies.request_model = (
            auth_post_request_model
        )
        auth_service_with_mocked_dependencies.request_model.scope = (
            "incorrect_scope"
        )
        with pytest.raises(ClientScopesError):
            await auth_service_with_mocked_dependencies._validate_scope()

    @patch.object(
        AuthorizationService, "_validate_scope", new_callable=AsyncMock
    )
    async def test_validate_auth_data(
        self,
        _validate_scope_mock,
        auth_service_with_mocked_dependencies,
        auth_post_request_model,
    ):
        auth_service_with_mocked_dependencies.request_model = (
            auth_post_request_model
        )
        result = (
            await auth_service_with_mocked_dependencies._validate_auth_data()
        )
        assert result is 1

    @patch("secrets.token_urlsafe")
    async def test_get_redirect_url_code_response_type(
        self,
        token_urlsafe_mock,
        auth_service_with_mocked_dependencies,
        auth_post_request_model,
    ):
        auth_service_with_mocked_dependencies.request_model = (
            auth_post_request_model
        )
        token_urlsafe_mock.return_value = "test_code"
        redirect_url = (
            await auth_service_with_mocked_dependencies.get_redirect_url()
        )
        assert (
            redirect_url
            == "https://test.com/redirect?code=test_code&state=test_state"
        )


@pytest.mark.asyncio
class TestResponseTypeHandlers:
    @patch(
        "src.business_logic.services.authorization.response_type_handlers.token.get_single_token",
        new_callable=AsyncMock,
    )
    async def test_get_redirect_url_token(
        self,
        get_single_token_mock,
        token_response_type_handler,
    ):
        token_mock = "test_token"
        get_single_token_mock.return_value = token_mock
        redirect_url = await token_response_type_handler.get_redirect_url(
            user_id=1
        )
        assert (
            redirect_url
            == f"https://test.com/redirect?access_token={token_mock}"
            "&token_type=Bearer&expires_in=600&state=test_state"
        )

    @patch(
        "src.business_logic.services.authorization.response_type_handlers.id_token.get_single_token",
        new_callable=AsyncMock,
    )
    async def test_get_redirect_url_id_token(
        self, get_single_token_mock, id_token_response_type_handler
    ):
        token_mock = "test_token"
        get_single_token_mock.return_value = token_mock
        redirect_url = await id_token_response_type_handler.get_redirect_url(
            user_id=1
        )
        assert (
            redirect_url
            == f"https://test.com/redirect?id_token={token_mock}&state=test_state"
        )


# ! Depracated
@pytest.mark.asyncio
class TestAuth:
    async def test_get_redirect_url_id_token_token(
        self,
        authorization_service: AuthorizationService,
        authorization_post_request_model: DataRequestModel,
    ) -> None:
        authorization_post_request_model.response_type = "id_token token"
        service = authorization_service
        service.request_model = authorization_post_request_model
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
        self,
        authorization_service: AuthorizationService,
        authorization_post_request_model: DataRequestModel,
    ) -> None:
        service = authorization_service
        service.request_model = authorization_post_request_model
        service.request_model.client_id = "not_exist_client"
        with pytest.raises(ClientNotFoundError):
            await service.get_redirect_url()

    async def test_get_redirect_url_without_scope(
        self,
        authorization_service: AuthorizationService,
        authorization_post_request_model: DataRequestModel,
    ) -> None:
        service = authorization_service
        service.request_model = authorization_post_request_model
        service.request_model.scope = None
        result = await service.get_redirect_url()
        assert result is None

    async def test_get_redirect_url_id_without_request_model(
        self, authorization_service: AuthorizationService
    ) -> None:
        service = authorization_service
        result = await service.get_redirect_url()
        assert result is None

    async def test_validate_client(
        self,
        authorization_service: AuthorizationService,
        connection: AsyncEngine,
    ) -> None:
        # The sequence id number is out of sync and raises duplicate key error
        # We manually bring it back in sync
        await connection.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('clients', 'id'), (SELECT MAX(id) FROM clients)+1);"
            )
        )
        await connection.execute(insert(Client).values(**DEFAULT_CLIENT))
        await connection.commit()
        authorization_service.request_model = DataRequestModel(
            client_id="h", response_type="u", redirect_uri="y"
        )
        client = await authorization_service._validate_client(
            client_id="default_test_client"
        )
        assert bool(client) is True
        await connection.execute(
            delete(Client).where(Client.client_id == "default_test_client")
        )
        await connection.commit()

    async def test_validate_client_error(
        self, authorization_service: AuthorizationService
    ) -> None:
        with pytest.raises(ClientNotFoundError):
            authorization_service.request_model = DataRequestModel(
                client_id="h", response_type="u", redirect_uri="y"
            )
            await authorization_service._validate_client(
                client_id="test_client_not_exist"
            )

    async def test_parse_scope_data(
        self, authorization_service: AuthorizationService
    ) -> None:
        expected_password = "BestOfTheBest"
        expected_client_id = "tony_stark"
        expected_username = "IronMan"

        to_parse = "gcp-api%20IdentityServerApi&client_id=tony_stark&password=BestOfTheBest&username=IronMan"
        result = await authorization_service._parse_scope_data(to_parse)
        assert result["client_id"] == expected_client_id
        assert result["password"] == expected_password
        assert result["username"] == expected_username

    async def test_parse_scope_data_len_two(
        self, authorization_service: AuthorizationService
    ) -> None:
        expected_password = "BestOfTheBest"
        expected_username = "IronMan"

        to_parse = "password=BestOfTheBest&username=IronMan"
        result = await authorization_service._parse_scope_data(to_parse)
        assert result["password"] == expected_password
        assert result["username"] == expected_username

    async def test_parse_empty_scope(
        self, authorization_service: AuthorizationService
    ) -> None:
        expected: dict[str, Any] = {}
        to_parse = ""
        result = await authorization_service._parse_scope_data(to_parse)
        assert result == expected

    async def test_parse_scope_without_separator(
        self, authorization_service: AuthorizationService
    ) -> None:
        expected = {"some_key": "key"}
        to_parse = "some_key=key"
        result = await authorization_service._parse_scope_data(to_parse)
        assert result == expected

    async def test_update_redirect_url_with_state(
        self,
        authorization_service: AuthorizationService,
        authorization_post_request_model: DataRequestModel,
    ) -> None:
        authorization_service.request_model = authorization_post_request_model
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
        self,
        authorization_service: AuthorizationService,
        authorization_post_request_model: DataRequestModel,
    ) -> None:
        authorization_service.request_model = authorization_post_request_model
        authorization_service.request_model.state = None
        expected_url = "https://www.google.com/?code=secret"
        redirect_url = (
            await authorization_service._update_redirect_url_with_params(
                "secret"
            )
        )

        assert redirect_url == expected_url

    async def test_get_redirect_url_code_response_type(
        self,
        authorization_service: AuthorizationService,
        authorization_post_request_model: DataRequestModel,
    ) -> None:
        expected_start = "https://www.google.com/"
        authorization_service.request_model = authorization_post_request_model
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
        self,
        authorization_service: AuthorizationService,
        authorization_post_request_model: DataRequestModel,
    ) -> None:
        expected_start = "https://www.google.com/"
        authorization_post_request_model.response_type = "token"
        authorization_service.request_model = authorization_post_request_model
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
        self,
        authorization_service: AuthorizationService,
        authorization_post_request_model: DataRequestModel,
    ) -> None:
        expected_start = "https://www.google.com/"
        authorization_post_request_model.response_type = "id_token token"
        authorization_service.request_model = authorization_post_request_model
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
