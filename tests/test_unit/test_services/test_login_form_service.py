import pytest

from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientRedirectUriError,
    WrongResponseTypeError,
)
from tests.test_unit.fixtures import authorization_request_model


@pytest.mark.asyncio
class TestLoginFormService:
    async def test_validate_client(self, login_form_service):
        client = await login_form_service._validate_client(
            client_id="thor"
        )
        assert client is True

    async def test_validate_client_error(self, login_form_service):
        with pytest.raises(ClientNotFoundError):
            await login_form_service._validate_client(
                client_id="test_client_not_exist"
            )

    async def test_validate_client_redirect_uri(self, login_form_service):
        uri = await login_form_service._validate_client_redirect_uri(
            client_id="santa",
            redirect_uri="https://www.google.com/"
        )
        assert uri is True

    async def test_validate_client_redirect_uri_error(self, login_form_service):
        with pytest.raises(ClientRedirectUriError):
            await login_form_service._validate_client_redirect_uri(
                client_id="santa",
                redirect_uri="no_uri"
            )

    async def test_get_html_form(self, login_form_service, authorization_request_model):
        service = login_form_service
        service.request_model = authorization_request_model
        result = await service.get_html_form()
        assert result is True

    async def test_get_html_form_wrong_response_type(self, login_form_service, authorization_request_model):
        authorization_request_model.response_type = "some type"
        service = login_form_service
        service.request_model = authorization_request_model
        with pytest.raises(WrongResponseTypeError):
            await service.get_html_form()
