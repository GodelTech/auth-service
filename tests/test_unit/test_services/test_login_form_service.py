import pytest
from sqlalchemy import delete, insert

from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientRedirectUriError,
    WrongResponseTypeError,
)
from src.data_access.postgresql.tables import IdentityProviderMapped
from tests.test_unit.fixtures import authorization_request_model


@pytest.mark.asyncio
class TestLoginFormService:
    async def test_validate_client(self, login_form_service):
        client = await login_form_service._validate_client(client_id="thor")
        assert client is True

    async def test_validate_client_error(self, login_form_service):
        with pytest.raises(ClientNotFoundError):
            await login_form_service._validate_client(
                client_id="test_client_not_exist"
            )

    async def test_validate_client_redirect_uri(self, login_form_service):
        uri = await login_form_service._validate_client_redirect_uri(
            client_id="santa", redirect_uri="https://www.google.com/"
        )
        assert uri is True

    async def test_validate_client_redirect_uri_error(
        self, login_form_service
    ):
        with pytest.raises(ClientRedirectUriError):
            await login_form_service._validate_client_redirect_uri(
                client_id="santa", redirect_uri="no_uri"
            )

    async def test_get_html_form(
        self, login_form_service, authorization_request_model
    ):
        service = login_form_service
        service.request_model = authorization_request_model
        result = await service.get_html_form()
        assert result is True

    async def test_get_html_form_wrong_response_type(
        self, login_form_service, authorization_request_model
    ):
        authorization_request_model.response_type = "some type"
        service = login_form_service
        service.request_model = authorization_request_model
        with pytest.raises(WrongResponseTypeError):
            await service.get_html_form()

    async def test_form_providers_data_for_auth(
        self, login_form_service, authorization_request_model, connection
    ):
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=1,
                provider_client_id="test_client",
                provider_client_secret="secret",
                enabled=True,
            )
        )
        await connection.commit()

        service = login_form_service
        service.request_model = authorization_request_model
        providers_data = await service.form_providers_data_for_auth()
        assert len(providers_data) == 1
        assert providers_data["github"]["provider_icon"] == "fa-github"
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.provider_client_id == "test_client"
            )
        )
        await connection.commit()

    async def test_form_providers_data_for_auth_no_providers(
        self,
        login_form_service,
        authorization_request_model,
    ):
        service = login_form_service
        service.request_model = authorization_request_model
        providers_data = await service.form_providers_data_for_auth()
        assert len(providers_data) == 0
        assert providers_data == {}

    async def test_form_providers_data_for_auth_not_registered_client(
        self,
        login_form_service,
        authorization_request_model,
    ):
        service = login_form_service
        service.request_model = authorization_request_model
        service.request_model.client_id = "not_registered_client"
        with pytest.raises(ClientNotFoundError):
            await service.form_providers_data_for_auth()

    async def test_form_providers_data_for_auth_no_request_model(
        self, login_form_service
    ):
        service = login_form_service
        providers_data = await service.form_providers_data_for_auth()
        assert providers_data is None

    async def test_get_html_form_no_request_model(self, login_form_service):
        service = login_form_service
        result = await service.get_html_form()
        assert result is None
