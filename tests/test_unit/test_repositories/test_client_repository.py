import uuid
from unittest.mock import AsyncMock

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exists, select, insert, update, delete, text

import pytest
from sqlalchemy.orm import sessionmaker

from data_access.postgresql.errors import DuplicationError
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

from src.data_access.postgresql.tables.client import (
    Client,
    ClientClaim,
    ClientPostLogoutRedirectUri,
    ClientRedirectUri,
    ClientScope,
    ClientSecret,
    AccessTokenType,
    RefreshTokenExpirationType,
    RefreshTokenUsageType,
    ResponseType,
    clients_response_types,
    clients_grant_types,
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

    async def test_validate_post_logout_redirect_uri_not_exists(self, engine: AsyncEngine) -> None:
        client_repo_error = ClientRepository(engine)
        with pytest.raises(ClientPostLogoutRedirectUriError):
            await client_repo_error.validate_post_logout_redirect_uri(
                client_id="test_client",
                logout_redirect_uri="http://redirect-uri-not-exists.com/",
            )

    async def test_validate_client_redirect_uri(self,
                                                engine: AsyncEngine,
                                                monkeypatch) -> None:
        mock_get_client_by_client_id = AsyncMock()
        mock_get_client_by_client_id.return_value = AsyncMock(id=1)
        monkeypatch.setattr(ClientRepository,
                            "get_client_by_client_id",
                            mock_get_client_by_client_id)
        client_repo = ClientRepository(engine)
        uri = await client_repo.validate_client_redirect_uri(
            client_id="test_client", redirect_uri="https://www.google.com/"
        )
        assert uri is True

    async def test_validate_client_redirect_uri_error(self,
                                                      engine: AsyncEngine,
                                                      monkeypatch) -> None:
        mock_get_client_by_client_id = AsyncMock()
        mock_get_client_by_client_id.return_value = AsyncMock(id=1)
        monkeypatch.setattr(ClientRepository,
                            "get_client_by_client_id",
                            mock_get_client_by_client_id)
        client_repo = ClientRepository(engine)
        with pytest.raises(ClientRedirectUriError):
            await client_repo.validate_client_redirect_uri(
                client_id="test_client", redirect_uri="just_uri"
            )

    async def test_get_client_scopes(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        uri = await client_repo.get_client_scopes(
            client_id=1
        )
        assert isinstance(uri, str)
        assert len(uri) > 0
        assert uri == "openid"

    async def test_get_client_scopes_not_exists(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        with pytest.raises(Exception):
            await client_repo.get_client_scopes(client_id=999)

    async def test_get_client_redirect_uris(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        result = await client_repo.get_client_redirect_uris(client_id=1)

        assert isinstance(result, list)
        assert all(isinstance(uri, str) for uri in result)
        assert len(result) > 0

    async def test_get_client_redirect_uris_not_exists(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        result = await client_repo.get_client_redirect_uris(client_id=999)

        assert isinstance(result, list)
        assert len(result) == 0

######################async def test_get_client_claims#################################
    # test_client = (await session.execute(
    #     select(Client).where(Client.client_id == "test_client")
    # )).scalar_one_or_none()
    # test_client_claim = ClientClaim(type="",
    #                                 value="",
    #                                 client_id=1,
    #                                 client=test_client)
    # session.add(test_client_claim)

    async def test_get_client_claims(self, engine: AsyncEngine) -> None:
        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            params = {"type": "",
                      "value": "",
                      "client_id": 1}
            await session.execute(insert(ClientClaim).values(**params))
            await session.commit()

        client_repo = ClientRepository(engine)
        result = await client_repo.get_client_claims(client_id=1)

        assert isinstance(result, list)
        assert all(isinstance(uri, str) for uri in result)
        assert len(result) > 0

    async def test_get_client_claims_not_exists(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        result = await client_repo.get_client_claims(client_id=999)

        assert isinstance(result, list)
        assert len(result) == 0


    async def test_create(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        unique_client_id = f"registration_test_client_{uuid.uuid4()}"
        params = {
            "client_id": "registration_test_client",
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2, #
            "refresh_token_expiration_type_id": 1, #
            "access_token_type_id": 1, #
            "protocol_type_id": 1, #

        }

        await client_repo.create(params)

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            client = await session.execute(
                select(Client).where(Client.client_id == "registration_test_client")
            )

            client = client.scalar_one_or_none()
            assert client is not None
            assert client.client_id == "registration_test_client"
            assert client.client_name == "regtestent"
            assert client.client_uri == "http://regtestent.com/"


    # async def test_create_with_incorrect_parameters(self, engine: AsyncEngine) -> None:
    #     client_repo = ClientRepository(engine)
    #     params = {
    #         "client_id": "test_client",
    #         "client_name": "regtestent",
    #         "client_uri": "http://regtestent.com/",
    #         "logo_uri": "https://www.regtestent-logo.com/",
    #         "token_endpoint_auth_method": "client_secret_post",
    #         "require_consent": False,
    #         "require_pkce": True,
    #         "refresh_token_usage_type_id": 2, #
    #         "refresh_token_expiration_type_id": 1, #
    #         "access_token_type_id": 1, #
    #         "protocol_type_id": 1, #
    #
    #     }
    #
    #     with pytest.raises(DuplicationError):
    #         await client_repo.create(params)













