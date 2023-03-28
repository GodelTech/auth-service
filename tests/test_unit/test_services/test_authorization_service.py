from unittest.mock import AsyncMock, MagicMock, Mock, patch
import pytest_asyncio
import pytest
from src.dyna_config import BASE_URL

from src.business_logic.services.authorization.authorization_service import (
    AuthorizationService,
)
from src.business_logic.services.authorization.response_type_handlers import (
    TokenResponseTypeHandler,
    IdTokenResponseType,
    IdTokenTokenResponseTypeHandler,
    DeviceCodeResponseTypeHandler,
    ResponseTypeHandlerBase,
    TokenResponseTypeHandlerBase,
    ResponseTypeHandler,
)
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientScopesError,
    WrongPasswordError,
)
from tests.test_unit.fixtures import (  # TODO shouldn't it be just in conftest files?
    DEFAULT_CLIENT,
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
def token_response_type_handler(
    auth_service_with_post_request_model_and_mocked_dependencies,
):
    handler = TokenResponseTypeHandler(
        auth_service_with_post_request_model_and_mocked_dependencies
    )
    yield handler
    del handler


@pytest.fixture
def id_token_response_type_handler(
    auth_service_with_post_request_model_and_mocked_dependencies,
):
    handler = IdTokenResponseType(
        auth_service_with_post_request_model_and_mocked_dependencies
    )
    yield handler
    del handler


@pytest.fixture
def id_token_token_response_type_handler(
    auth_service_with_post_request_model_and_mocked_dependencies,
):
    handler = IdTokenTokenResponseTypeHandler(
        auth_service_with_post_request_model_and_mocked_dependencies
    )
    yield handler
    del handler


@pytest.fixture
def device_code_response_type_handler(
    auth_service_with_post_request_model_and_mocked_dependencies,
):
    handler = DeviceCodeResponseTypeHandler(
        auth_service_with_post_request_model_and_mocked_dependencies
    )
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
        self, auth_service_with_post_request_model_and_mocked_dependencies
    ):
        await auth_service_with_post_request_model_and_mocked_dependencies._validate_scope()

    async def test_validate_scope_with_incorrect_scope(
        self, auth_service_with_post_request_model_and_mocked_dependencies
    ):
        auth_service_with_post_request_model_and_mocked_dependencies.request_model.scope = (
            "incorrect_scope"
        )
        with pytest.raises(ClientScopesError):
            await auth_service_with_post_request_model_and_mocked_dependencies._validate_scope()

    @patch.object(
        AuthorizationService, "_validate_scope", new_callable=AsyncMock
    )
    async def test_validate_auth_data(
        self,
        _validate_scope_mock,
        auth_service_with_post_request_model_and_mocked_dependencies,
    ):
        result = (
            await auth_service_with_post_request_model_and_mocked_dependencies._validate_auth_data()
        )
        assert result is 1

    async def test_validate_auth_data_invalid_password(
        self, auth_service_with_post_request_model_and_mocked_dependencies
    ):
        auth_service_with_post_request_model_and_mocked_dependencies.user_repo.get_hash_password.side_effect = (
            WrongPasswordError
        )
        with pytest.raises(WrongPasswordError):
            await auth_service_with_post_request_model_and_mocked_dependencies._validate_auth_data()

    @patch("secrets.token_urlsafe")
    async def test_get_redirect_url(
        self,
        token_urlsafe_mock,
        auth_service_with_post_request_model_and_mocked_dependencies,
    ):
        token_urlsafe_mock.return_value = "test_code"
        redirect_url = (
            await auth_service_with_post_request_model_and_mocked_dependencies.get_redirect_url()
        )
        assert (
            redirect_url
            == "https://test.com/redirect?code=test_code&state=test_state"
        )


@pytest.mark.asyncio
class TestTokenResponseTypeHandler:
    @patch(
        "src.business_logic.services.authorization.response_type_handlers.token.get_single_token",
        new_callable=AsyncMock,
    )
    async def test_get_redirect_url(
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


# ! Depracated

#     async def test_update_redirect_url_with_state(
#         self,
#         authorization_service: AuthorizationService,
#         authorization_post_request_model: DataRequestModel,
#     ) -> None:
#         authorization_service.request_model = authorization_post_request_model
#         expected_url = "https://www.google.com/?code=secret&state=state"
#         redirect_url = (
#             await authorization_service._update_redirect_url_with_params(
#                 "secret"
#             )
#         )

#         assert redirect_url == expected_url

#     async def test_update_redirect_url_without_request_model(
#         self, authorization_service: AuthorizationService
#     ) -> None:
#         result = await authorization_service._update_redirect_url_with_params(
#             "secret"
#         )
#         assert result is None

#     async def test_update_redirect_url_without_state(
#         self,
#         authorization_service: AuthorizationService,
#         authorization_post_request_model: DataRequestModel,
#     ) -> None:
#         authorization_service.request_model = authorization_post_request_model
#         authorization_service.request_model.state = None
#         expected_url = "https://www.google.com/?code=secret"
#         redirect_url = (
#             await authorization_service._update_redirect_url_with_params(
#                 "secret"
#             )
#         )

#         assert redirect_url == expected_url

#     async def test_get_redirect_url_code_response_type(
#         self,
#         authorization_service: AuthorizationService,
#         authorization_post_request_model: DataRequestModel,
#     ) -> None:
#         expected_start = "https://www.google.com/"
#         authorization_service.request_model = authorization_post_request_model
#         result_uri = (
#             await authorization_service.get_redirect_url_code_response_type(
#                 user_id=2
#             )
#         )
#         if not result_uri:
#             raise AssertionError
#         if not result_uri:
#             raise AssertionError
#         start_uri = result_uri.split("?")[0]
#         data = {
#             item.split("=")[0]: item.split("=")[1]
#             for item in result_uri.split("?")[1].split("&")
#         }

#         assert start_uri == expected_start
#         assert data["state"] == "state"
#         assert "access_token" not in data
#         assert "code" in data

#         await authorization_service.persistent_grant_repo.delete(
#             grant_data=data["code"], grant_type="code"
#         )

#     async def test_get_redirect_url_code_response_type_without_request_model(
#         self, authorization_service: AuthorizationService
#     ) -> None:
#         result = (
#             await authorization_service.get_redirect_url_code_response_type(
#                 user_id=2
#             )
#         )
#         assert result is None

#     async def test_get_redirect_url_device_code_response_type_without_request_model(
#         self, authorization_service: AuthorizationService
#     ) -> None:
#         result = await authorization_service.get_redirect_url_device_code_response_type(
#             user_id=2
#         )
#         assert result is None

#     async def test_get_redirect_url_token_response_type(
#         self,
#         authorization_service: AuthorizationService,
#         authorization_post_request_model: DataRequestModel,
#     ) -> None:
#         expected_start = "https://www.google.com/"
#         authorization_post_request_model.response_type = "token"
#         authorization_service.request_model = authorization_post_request_model
#         result_uri = (
#             await authorization_service.get_redirect_url_token_response_type(
#                 user_id=2
#             )
#         )
#         if not result_uri:
#             raise AssertionError
#         start_uri = result_uri.split("?")[0]
#         data = {
#             item.split("=")[0]: item.split("=")[1]
#             for item in result_uri.split("?")[1].split("&")
#         }
#         assert start_uri == expected_start
#         assert "access_token" in data
#         assert "id_token" not in data
#         assert data["token_type"] in "Bearer"

#     async def test_get_redirect_url_token_response_type_without_request_model(
#         self, authorization_service: AuthorizationService
#     ) -> None:
#         result = (
#             await authorization_service.get_redirect_url_token_response_type(
#                 user_id=2
#             )
#         )
#         assert result is None

#     async def test_get_redirect_url_id_token_token_response_type(
#         self,
#         authorization_service: AuthorizationService,
#         authorization_post_request_model: DataRequestModel,
#     ) -> None:
#         expected_start = "https://www.google.com/"
#         authorization_post_request_model.response_type = "id_token token"
#         authorization_service.request_model = authorization_post_request_model
#         result_uri = await authorization_service.get_redirect_url_id_token_token_response_type(
#             user_id=2
#         )
#         if not result_uri:
#             raise AssertionError
#         start_uri = result_uri.split("?")[0]
#         data = {
#             item.split("=")[0]: item.split("=")[1]
#             for item in result_uri.split("?")[1].split("&")
#         }
#         assert start_uri == expected_start
#         assert "access_token" in data
#         assert "id_token" in data
#         assert data["token_type"] in "Bearer"

#     async def test_get_redirect_url_id_token_token_response_type_without_request_model(
#         self, authorization_service: AuthorizationService
#     ) -> None:
#         result = await authorization_service.get_redirect_url_id_token_token_response_type(
#             user_id=2
#         )
#         assert result is None
