from unittest.mock import AsyncMock, patch, Mock
import pytest_asyncio
import pytest
from src.dyna_config import BASE_URL

from src.business_logic.services.authorization.authorization_service import (
    AuthorizationService,
)
from src.business_logic.services.authorization.response_type_handlers import (
    TokenResponseTypeHandler,
    IdTokenResponseTypeHandler,
    IdTokenTokenResponseTypeHandler,
    DeviceCodeResponseTypeHandler,
    ResponseTypeHandlerBase,
    ResponseTypeHandler,
    ResponseTypeHandlerFactory,
)
from src.data_access.postgresql.errors import (
    UserNotFoundError,
    ClientNotFoundError,
    ClientScopesError,
    WrongPasswordError,
    WrongResponseTypeError,
)
from tests.test_unit.fixtures import (  # TODO shouldn't it be just in conftest files?
    auth_post_request_model,
)


@pytest_asyncio.fixture
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
def auth_service_with_post_request_model_and_mocked_dependencies(
    auth_service_with_mocked_dependencies, auth_post_request_model
):
    auth_service_with_mocked_dependencies.request_model = (
        auth_post_request_model
    )
    yield auth_service_with_mocked_dependencies
    del auth_service_with_mocked_dependencies


@pytest.fixture
def response_type_handler(
    auth_service_with_post_request_model_and_mocked_dependencies,
):
    def create_handler(handler_class):
        handler = handler_class(
            auth_service_with_post_request_model_and_mocked_dependencies
        )
        yield handler
        del handler

    return create_handler


@pytest.fixture
def token_response_type_handler(response_type_handler):
    yield from response_type_handler(TokenResponseTypeHandler)


@pytest.fixture
def id_token_response_type_handler(response_type_handler):
    yield from response_type_handler(IdTokenResponseTypeHandler)


@pytest.fixture
def id_token_token_response_type_handler(response_type_handler):
    yield from response_type_handler(IdTokenTokenResponseTypeHandler)


@pytest.fixture
def device_code_response_type_handler(response_type_handler):
    yield from response_type_handler(DeviceCodeResponseTypeHandler)


@pytest.fixture
def response_type_handler_base(response_type_handler):
    yield from response_type_handler(ResponseTypeHandlerBase)


@pytest.fixture
def response_type_handler_factory():
    factory = ResponseTypeHandlerFactory()
    yield factory
    del factory


@pytest.mark.asyncio
class TestAuthorizationService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        auth_service_with_post_request_model_and_mocked_dependencies,
    ):
        self.auth_service = (
            auth_service_with_post_request_model_and_mocked_dependencies
        )

    async def test_request_model_not_provided(self):
        self.auth_service.request_model = None
        with pytest.raises(ValueError):
            self.auth_service.request_model

    async def test_validate_scope(self):
        await self.auth_service._validate_scope()

    async def test_validate_scope_with_invalid_scope(self):
        self.auth_service.request_model.scope = "invalid_scope"
        with pytest.raises(ClientScopesError):
            await self.auth_service._validate_scope()

    @patch.object(
        AuthorizationService, "_validate_scope", new_callable=AsyncMock
    )
    async def test_validate_auth_data(self, _validate_scope_mock):
        user_id = 1
        result = await self.auth_service._validate_auth_data()
        assert result == user_id

    async def test_validate_auth_data_invalid_password(self):
        self.auth_service.password_service.validate_password.side_effect = (
            WrongPasswordError
        )
        with pytest.raises(WrongPasswordError):
            await self.auth_service._validate_auth_data()

    async def test_validate_auth_data_invalid_client(self):
        self.auth_service.client_repo.validate_client_redirect_uri.side_effect = (
            ClientNotFoundError
        )
        with pytest.raises(ClientNotFoundError):
            await self.auth_service._validate_auth_data()

    async def test_validate_auth_data_invalid_username(self):
        self.auth_service.user_repo.get_hash_password.side_effect = (
            UserNotFoundError
        )
        with pytest.raises(UserNotFoundError):
            await self.auth_service._validate_auth_data()

    @patch("secrets.token_urlsafe")
    async def test_get_redirect_url(self, token_urlsafe_mock):
        token_urlsafe_mock.return_value = "test_code"
        redirect_url = await self.auth_service.get_redirect_url()
        assert (
            redirect_url
            == "https://test.com/redirect?code=test_code&state=test_state"
        )

    async def test_get_redirect_url_invalid_response_type(self):
        self.auth_service.request_model.response_type = "invalid_response_type"
        with pytest.raises(WrongResponseTypeError):
            await self.auth_service.get_redirect_url()


@pytest.mark.asyncio
class TestTokenResponseTypeHandler:
    @patch(
        "src.business_logic.services.authorization.response_type_handlers.token.get_single_token",
        new_callable=AsyncMock,
    )
    async def test_get_redirect_url(
        self, get_single_token_mock, token_response_type_handler
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
        assert isinstance(
            token_response_type_handler,
            (
                ResponseTypeHandler,
                ResponseTypeHandlerBase,
                TokenResponseTypeHandler,
            ),
        )


@pytest.mark.asyncio
class TestIdTokenResponseTypeHandler:
    @patch(
        "src.business_logic.services.authorization.response_type_handlers.id_token.get_single_token",
        new_callable=AsyncMock,
    )
    async def test_get_redirect_url(
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
        assert isinstance(
            id_token_response_type_handler,
            (
                ResponseTypeHandler,
                ResponseTypeHandlerBase,
                TokenResponseTypeHandler,
            ),
        )


@pytest.mark.asyncio
class TestIdTokenTokenResponseTypeHandler:
    @patch(
        "src.business_logic.services.authorization.response_type_handlers.id_token_token.get_single_token",
        new_callable=AsyncMock,
    )
    async def test_get_redirect_url(
        self, get_single_token_mock, id_token_token_response_type_handler
    ):
        token_mock = "test_token"
        get_single_token_mock.return_value = token_mock
        redirect_url = (
            await id_token_token_response_type_handler.get_redirect_url(
                user_id=1
            )
        )
        assert (
            redirect_url
            == f"https://test.com/redirect?access_token={token_mock}"
            f"&token_type=Bearer&expires_in=600&id_token={token_mock}&state=test_state"
        )
        assert isinstance(
            id_token_token_response_type_handler,
            (
                ResponseTypeHandler,
                ResponseTypeHandlerBase,
                TokenResponseTypeHandler,
            ),
        )


@pytest.mark.asyncio
class TestDeviceResponseTypeHandler:
    @patch.object(
        DeviceCodeResponseTypeHandler,
        "_parse_scope_data",
        new_callable=AsyncMock,
    )
    async def test_get_redirect_url(
        self, _parse_scope_data_mock, device_code_response_type_handler
    ):
        _parse_scope_data_mock.return_value = {"user_code": 1}
        redirect_url = (
            await device_code_response_type_handler.get_redirect_url(user_id=1)
        )
        assert redirect_url == f"http://{BASE_URL}/device/auth/success"

    # TODO change it after fixing the _parse_scope_data method
    async def test_parse_scope_data(self, device_code_response_type_handler):
        scope = "foo=bar&baz=quz"
        scope = "foo=bar&baz=qux"
        expected_output = {"foo": "bar", "baz": "qux"}
        assert (
            await device_code_response_type_handler._parse_scope_data(scope)
            == expected_output
        )
        assert isinstance(
            device_code_response_type_handler,
            (
                ResponseTypeHandler,
                ResponseTypeHandlerBase,
            ),
        )


@pytest.mark.asyncio
class TestResponseTypeHandlerBase:
    async def test_update_redirect_url_with_state(
        self, response_type_handler_base
    ):
        redirect_url = "https://www.test.com/redirect?test_param=test"
        result = await response_type_handler_base._update_redirect_url(
            redirect_url=redirect_url
        )
        assert result == f"{redirect_url}&state=test_state"

    async def test_update_redirect_url_without_state(
        self, response_type_handler_base
    ):
        response_type_handler_base.auth_service.request_model.state = None
        redirect_url = "https://www.test.com/redirect?test_param=test"
        result = await response_type_handler_base._update_redirect_url(
            redirect_url=redirect_url
        )
        assert result == redirect_url


class TestResponseTypeHandlerFactory:
    @pytest.fixture(autouse=True)
    def setup(self, response_type_handler_factory):
        self.factory = response_type_handler_factory

    def test_register_handler(self):
        self.factory.register_handler("test", TokenResponseTypeHandler)
        assert self.factory._handlers["test"] == TokenResponseTypeHandler

    def test_get_handler(self):
        self.factory.register_handler("test", TokenResponseTypeHandler)
        auth_service = Mock(spec=AuthorizationService)
        handler = self.factory.get_handler("test", auth_service)
        assert isinstance(handler, TokenResponseTypeHandler)
        assert handler.auth_service == auth_service

    def test_get_non_existing_handler(self):
        with pytest.raises(WrongResponseTypeError):
            self.factory.get_handler("non_existing_handler", None)
