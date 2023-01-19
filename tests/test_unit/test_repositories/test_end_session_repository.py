import pytest

from src.data_access.postgresql.errors.client import ClientPostLogoutRedirectUriError
from src.data_access.postgresql.repositories.client import ClientPostLogoutRedirectUriRepository


@pytest.mark.asyncio
class TestClientRepository:

    async def test_validate_post_logout_redirect_uri(self, connection):
        client_logout_redirect_repo = ClientPostLogoutRedirectUriRepository(connection)

        redirect = await client_logout_redirect_repo. \
            validate_post_logout_redirect_uri(
                client_id='test_client',
                logout_redirect_uri='https://www.scott.org/'
            )
        assert redirect is True

    async def test_validate_post_logout_redirect_uri_not_exists(self, connection):
        client_repo_error = ClientPostLogoutRedirectUriRepository(connection)
        with pytest.raises(ClientPostLogoutRedirectUriError):
            await client_repo_error.validate_post_logout_redirect_uri(
                client_id='client_not_exist',
                logout_redirect_uri='test_uri_not_exist'
            )
