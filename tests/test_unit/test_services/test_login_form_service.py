import pytest
from sqlalchemy import delete, insert

from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientRedirectUriError,
    WrongResponseTypeError,
)
from src.data_access.postgresql.tables import IdentityProviderMapped
from tests.test_unit.fixtures import authorization_get_request_model
from src.business_logic.services.login_form_service import LoginFormService
from src.presentation.api.models import RequestModel
from sqlalchemy.ext.asyncio.engine import AsyncEngine


@pytest.mark.asyncio
class TestLoginFormService:
    async def test_validate_client(
        self, login_form_service: LoginFormService
    ) -> None:
        client = await login_form_service._validate_client(client_id="thor")
        assert client is True

    async def test_validate_client_error(
        self, login_form_service: LoginFormService
    ) -> None:
        with pytest.raises(ClientNotFoundError):
            await login_form_service._validate_client(
                client_id="test_client_not_exist"
            )

    async def test_validate_client_redirect_uri(
        self, login_form_service: LoginFormService
    ) -> None:
        uri = await login_form_service._validate_client_redirect_uri(
            client_id="santa", redirect_uri="https://www.google.com/"
        )
        assert uri is True

    async def test_validate_client_redirect_uri_error(
        self, login_form_service: LoginFormService
    ) -> None:
        with pytest.raises(ClientRedirectUriError):
            await login_form_service._validate_client_redirect_uri(
                client_id="santa", redirect_uri="no_uri"
            )

    async def test_get_html_form(
        self,
        login_form_service: LoginFormService,
        authorization_get_request_model: RequestModel,
    ) -> None:
        service = login_form_service
        service.request_model = authorization_get_request_model
        result = await service.get_html_form()
        assert result is True

    async def test_get_html_form_wrong_response_type(
        self,
        login_form_service: LoginFormService,
        authorization_get_request_model: RequestModel,
    ) -> None:
        authorization_get_request_model.response_type = "some type"
        service = login_form_service
        service.request_model = authorization_get_request_model
        with pytest.raises(WrongResponseTypeError):
            await service.get_html_form()

    async def test_form_providers_data_for_auth(
        self,
        login_form_service: LoginFormService,
        authorization_get_request_model: RequestModel,
        connection: AsyncEngine,
    ) -> None:
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
        service.request_model = authorization_get_request_model
        providers_data = await service.form_providers_data_for_auth()
        assert providers_data
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
        login_form_service: LoginFormService,
        authorization_get_request_model: RequestModel,
    ) -> None:
        service = login_form_service
        service.request_model = authorization_get_request_model
        providers_data = await service.form_providers_data_for_auth()
        assert providers_data is not None
        assert len(providers_data) == 0
        assert providers_data == {}

    async def test_form_providers_data_for_auth_not_registered_client(
        self,
        login_form_service: LoginFormService,
        authorization_get_request_model: RequestModel,
    ) -> None:
        service = login_form_service
        service.request_model = authorization_get_request_model
        service.request_model.client_id = "not_registered_client"
        with pytest.raises(ClientNotFoundError):
            await service.form_providers_data_for_auth()

    async def test_form_providers_data_for_auth_no_request_model(
        self, login_form_service: LoginFormService
    ) -> None:
        service = login_form_service
        providers_data = await service.form_providers_data_for_auth()
        assert providers_data is None

    async def test_get_html_form_no_request_model(
        self, login_form_service: LoginFormService
    ) -> None:
        service = login_form_service
        result = await service.get_html_form()
        assert result is None
