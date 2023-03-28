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
        params = {
            "client_id": "registration_test_client",
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2,
            "refresh_token_expiration_type_id": 1,
            "access_token_type_id": 1,
            "protocol_type_id": 1,

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


    async def test_create_with_incorrect_parameters(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        params = {
            "client_id": "test_client",
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2,
            "refresh_token_expiration_type_id": 1,
            "access_token_type_id": 1,
            "protocol_type_id": 1,

        }

        with pytest.raises(Exception):
            await client_repo.create(params)


    async def test_add_secret(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)

        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            # "id": 99,
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2,
            "refresh_token_expiration_type_id": 1,
            "access_token_type_id": 1,
            "protocol_type_id": 1,

        }

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            result = await session.execute(insert(Client).values(**new_client).returning(Client.id))
            client_id_int = result.scalar_one()
            # await session.execute(insert(Client).values(**new_client))
            # client_id_int = await session.
            await session.commit()

        await client_repo.add_secret(client_id_int=client_id_int, value="test_secret")

        async with session_factory() as session:
            secret = await session.execute(
                select(ClientSecret).where(ClientSecret.client_id == client_id_int)
            )
            secret = secret.scalar_one_or_none()

            assert secret is not None
            assert secret.client_id == client_id_int
            assert secret.value == "test_secret"

    async def test_add_secret_incorrect_parameters(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        with pytest.raises(Exception):
            await client_repo.add_secret(client_id_int=99, value="secret_test_secret")

    async def test_add_scope(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)

        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            # "id": 101,
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2,
            "refresh_token_expiration_type_id": 1,
            "access_token_type_id": 1,
            "protocol_type_id": 1,
        }

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            # await session.execute(insert(Client).values(**new_client))
            result = await session.execute(insert(Client).values(**new_client).returning(Client.id))
            client_id_int = result.scalar_one()
            await session.commit()

        await client_repo.add_scope(client_id_int=client_id_int, scope="test_scope")

        async with session_factory() as session:
            scope = await session.execute(
                select(ClientScope).where(ClientScope.client_id == client_id_int)
            )
            scope = scope.scalar_one_or_none()

            assert scope is not None
            assert scope.client_id == client_id_int
            assert scope.scope == "test_scope"

    async def test_add_scope_incorrect_parameters(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        with pytest.raises(Exception):
            await client_repo.add_scope(client_id_int=99, scope="test_scope")


    async def test_add_redirect_uris(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)

        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2,
            "refresh_token_expiration_type_id": 1,
            "access_token_type_id": 1,
            "protocol_type_id": 1,
        }

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            result = await session.execute(insert(Client).values(**new_client).returning(Client.id))
            client_id_int = result.scalar_one()
            await session.commit()

        insert_redirect_uris = ["https://www.google.com/", "https://www.facebook.com/"]
        await client_repo.add_redirect_uris(client_id_int=client_id_int,
                                            redirect_uris=insert_redirect_uris)

        async with session_factory() as session:
            # uris_object = await session.execute(
            #     select(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
            # )
            # # res_redirect_uris = [uri_obj.redirect_uri for uri_obj in uris_object.scalars()]
            # res_redirect_uris = [uri_obj[0].redirect_uri for uri_obj in uris_object.all()]

            uris_object = await session.scalars(
                select(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
            )
            res_redirect_uris = [uri_obj.redirect_uri for uri_obj in uris_object.all()]

            # uris = uris_object.scalar_one_or_none()

            assert res_redirect_uris is not None
            assert res_redirect_uris == insert_redirect_uris

    async def test_add_redirect_uris_incorrect_parameters(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        with pytest.raises(Exception):
            await client_repo.add_redirect_uris(client_id_int=99,
                                                redirect_uris=["https://www.google.com/"])

    async def test_get_access_token_type_id(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        result = await client_repo.get_access_token_type_id(str_type="jwt")
        id = 1
        assert isinstance(result, int)
        assert result == id

    async def test_get_access_token_type_id_not_exist(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        with pytest.raises(ValueError):
            await client_repo.get_access_token_type_id(str_type="not_exist")

    async def test_get_refresh_token_usage_type_id(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        result = await client_repo.get_refresh_token_usage_type_id(str_type="one_time_only")
        id = 1
        assert isinstance(result, int)
        assert result == id

    async def test_get_refresh_token_usage_type_id_not_exist(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        with pytest.raises(ValueError):
            await client_repo.get_refresh_token_usage_type_id(str_type="not_exist")

    async def test_get_refresh_token_expiration_type_id(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        result = await client_repo.get_refresh_token_expiration_type_id(str_type="absolute")
        id = 1
        assert isinstance(result, int)
        assert result == id

    async def test_get_refresh_token_expiration_type_id_not_exist(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)
        with pytest.raises(ValueError):
            await client_repo.get_refresh_token_expiration_type_id(str_type="not_exist")

    async def test_update(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)

        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2,
            "refresh_token_expiration_type_id": 1,
            "access_token_type_id": 1,
            "protocol_type_id": 1,
        }

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            await session.execute(insert(Client).values(**new_client).returning(Client.id))
            await session.commit()

        new_params = {
            "client_name": "regtestent_new",
            "client_uri": "https://regtestent-new.com/",
        }
        await client_repo.update(client_id=unique_client_id, **new_params)

        async with session_factory() as session:

            client_result = await session.scalars(
                select(Client).where(Client.client_id == unique_client_id)
            )
            client = client_result.first()

            assert client is not None
            assert isinstance(client, Client)
            assert client.client_name == "regtestent_new"
            assert client.client_uri == "https://regtestent-new.com/"

    async def test_update_non_existent_client_id(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)

        non_existent_client_id = "non_existent_client_id"
        update_data = {"client_name": "updated_client_name"}

        await client_repo.update(non_existent_client_id, **update_data)

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )

        async with session_factory() as session:
            client = await session.execute(
                select(Client).where(Client.client_id == non_existent_client_id)
            )
            client = client.scalar_one_or_none()

        assert client is None

    async def test_delete_scope(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)

        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2,
            "refresh_token_expiration_type_id": 1,
            "access_token_type_id": 1,
            "protocol_type_id": 1,
        }

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            result = await session.execute(insert(Client).values(**new_client).returning(Client.id))
            client_id_int = result.scalar_one()
            await session.execute(insert(ClientScope).values(
                client_id=client_id_int,
                scope="openid",
            ))
            await session.commit()

        async with session_factory() as session:
            scope = await session.execute(
                select(ClientScope).where(ClientScope.client_id == client_id_int)
            )
            scope = scope.scalar_one_or_none()

        assert scope is not None

        await client_repo.delete_scope(client_id_int=client_id_int)

        async with session_factory() as session:
            scope = await session.execute(
                select(ClientScope).where(ClientScope.client_id == client_id_int)
            )
            scope = scope.scalar_one_or_none()

            assert scope is None

    async def test_delete_redirect_uris(self, engine: AsyncEngine) -> None:
        client_repo = ClientRepository(engine)

        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret_post",
            "require_consent": False,
            "require_pkce": True,
            "refresh_token_usage_type_id": 2,
            "refresh_token_expiration_type_id": 1,
            "access_token_type_id": 1,
            "protocol_type_id": 1,
        }

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            result = await session.execute(insert(Client).values(**new_client).returning(Client.id))
            client_id_int = result.scalar_one()
            await session.execute(insert(ClientRedirectUri).values(
                client_id=client_id_int,
                redirect_uri="https://www.google.com/",
            ))
            await session.commit()

        async with session_factory() as session:
            redirect_uri = await session.execute(
                select(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
            )
            redirect_uri = redirect_uri.scalar_one_or_none()

        assert redirect_uri is not None

        await client_repo.delete_redirect_uris(client_id_int=client_id_int)

        async with session_factory() as session:
            redirect_uri = await session.execute(
                select(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
            )
            redirect_uri = redirect_uri.scalar_one_or_none()

            assert redirect_uri is None






























