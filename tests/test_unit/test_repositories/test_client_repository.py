import pytest

from src.data_access.postgresql.errors.client import (
    ClientNotFoundError,
    ClientRedirectUriError,
)
from src.data_access.postgresql.repositories.client import ClientRepository
from sqlalchemy.ext.asyncio import AsyncEngine

from src.data_access.postgresql.errors.client import (
    ClientNotFoundError,
    ClientPostLogoutRedirectUriError,
    ClientRedirectUriError,
)

@pytest.mark.asyncio
class TestClientRepository:
    async def test_get_client_by_client_id(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        client = await client_repo.get_client_by_client_id(
            client_id="test_client"
        )
        assert client.client_id == "test_client"

    async def test_get_client_by_client_id_not_exists(self, engine: AsyncEngine) -> None:
        client_repo_error = ClientRepository(engine)
        with pytest.raises(ClientNotFoundError):
            await client_repo_error.get_client_by_client_id(
                client_id="test_client_not_exist"
            )

    @pytest.mark.parametrize("client_id, boolean",
                             [("test_client", True),
                              ("test_client_not_exist", False)])
    async def test_validate_client_by_client_id(self, engine: AsyncEngine,
                                                client_id,
                                                boolean) -> None:
        client_repo = ClientRepository(engine)
        result = await client_repo.validate_client_by_client_id(
            client_id=client_id
        )
        assert result == boolean

    # validate_client_by_int_id differ for validate_client_by_client_id by
    # containing ClientNotFoundError. Do we need one? Check in docs: 
    # https://connect2id.com/products/server/docs/api/client-registration
    @pytest.mark.parametrize("int_id, boolean",
                             [(1, True),])
                              # (999, False)])
    async def test_validate_client_by_int_id(self, engine: AsyncEngine,
                                                int_id,
                                                boolean) -> None:
        client_repo = ClientRepository(engine)
        result = await client_repo.validate_client_by_int_id(
            client_id=int_id
        )
        assert result == boolean

    async def test_validate_client_by_int_id_not_exists(self, engine: AsyncEngine) -> None:
        client_repo_error = ClientRepository(engine)
        with pytest.raises(ClientNotFoundError):
            await client_repo_error.validate_client_by_int_id(
                client_id=999
            )

    async def test_get_client_secret_by_client_id(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        expected = "past"
        secret = await client_repo.get_client_secrete_by_client_id(
            client_id="test_client"
        )
        assert secret == expected

    async def test_get_client_secret_by_client_id_not_exists(self, engine: AsyncEngine) -> None:
        client_repo_error = ClientRepository(engine)
        with pytest.raises(ClientNotFoundError):
            await client_repo_error.get_client_secrete_by_client_id(
                client_id="test_client_not_exist"
            )

    async def test_validate_post_logout_redirect_uri(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        result = await client_repo.validate_post_logout_redirect_uri(
            client_id="test_client",
            logout_redirect_uri="http://thompson-chung.com/",
        )
        assert result

    #### !!!!!!!!!!!!!mock ClientPostLogoutRedirectUriError ########################
    async def test_validate_post_logout_redirect_uri_not_exists(self, engine: AsyncEngine) -> None:
        client_repo_error = ClientRepository(engine)
        with pytest.raises(ClientPostLogoutRedirectUriError):
            await client_repo_error.validate_post_logout_redirect_uri(
                client_id="test_client",
                logout_redirect_uri="http://redirect-uri-not-exists.com/",
            )

    async def test_validate_client_redirect_uri(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        uri = await client_repo.validate_client_redirect_uri(
            client_id="test_client", redirect_uri="https://www.google.com/"
        )
        assert uri is True

    async def test_validate_client_redirect_uri_error(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        with pytest.raises(ClientRedirectUriError):
            await client_repo.validate_client_redirect_uri(
                client_id="test_client", redirect_uri="just_uri"
            )


