import pytest

from src.data_access.postgresql.errors.client import ClientNotFoundError, ClientRedirectUriError
from src.data_access.postgresql.repositories.client import ClientRepository


@pytest.mark.asyncio
class TestClientRepository:
    async def test_get_client_by_client_id(self, engine):
        client_repo = ClientRepository(engine)
        client = await client_repo.get_client_by_client_id(
            client_id="test_client"
        )
        assert bool(client) is True

    async def test_get_client_by_client_id_not_exists(self, engine):
        client_repo_error = ClientRepository(engine)
        with pytest.raises(ClientNotFoundError):
            await client_repo_error.get_client_by_client_id(
                client_id="test_client_not_exist"
            )

    async def test_get_client_secret_by_client_id(self, engine):
        client_repo = ClientRepository(engine)
        expected = "past"
        secret = await client_repo.get_client_secrete_by_client_id(
            client_id="test_client"
        )
        assert secret == expected

    async def test_get_client_secret_by_client_id_not_exists(self, engine):
        client_repo_error = ClientRepository(engine)
        with pytest.raises(ClientNotFoundError):
            await client_repo_error.get_client_secrete_by_client_id(
                client_id="test_client_not_exist"
            )

    async def test_validate_client_redirect_uri(self, engine):
        client_repo = ClientRepository(engine)
        uri = await client_repo.validate_client_redirect_uri(
            client_id="test_client",
            redirect_uri="https://www.google.com/"
        )
        assert uri is True

    async def test_validate_client_redirect_uri_error(self, engine):
        client_repo = ClientRepository(engine)
        with pytest.raises(ClientRedirectUriError):
            await client_repo.validate_client_redirect_uri(
                client_id="test_client",
                redirect_uri="just_uri"
            )
