import pytest

from src.data_access.postgresql.errors.client import ClientPostLogoutRedirectUriError
from src.data_access.postgresql.repositories.client import ClientRepository


@pytest.mark.asyncio
class TestClientRepository:

    async def test_validate_post_logout_redirect_uri(self, engine):
        client_logout_redirect_repo = ClientRepository(engine)

        redirect = await client_logout_redirect_repo. \
            validate_post_logout_redirect_uri(
                client_id='test_client',
                logout_redirect_uri='http://campbell-taylor.net/'
            )
        assert redirect is True

    async def test_validate_post_logout_redirect_uri_not_exists(self, engine):
        client_repo_error = ClientRepository(engine)
        with pytest.raises(ClientPostLogoutRedirectUriError):
            await client_repo_error.validate_post_logout_redirect_uri(
                client_id='test_client',
                logout_redirect_uri='test_uri_not_exist'
            )
