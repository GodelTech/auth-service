import pytest

from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientRedirectUriError,
)


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
