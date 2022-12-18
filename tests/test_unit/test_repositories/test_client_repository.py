import pytest
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.errors.client import ClientNotFoundError


@pytest.mark.asyncio
class TestClientRepository:

    async def test_get_client_by_client_id(self, connection):
        client_repo = ClientRepository(connection)
        client = await client_repo.get_client_by_client_id(client_id='test_client')
        assert client is True

    async def test_get_client_by_client_id_not_exists(self, connection):
        client_repo_error = ClientRepository(connection)
        with pytest.raises(ClientNotFoundError):
            await client_repo_error.get_client_by_client_id(client_id='test_client_not_exist')
