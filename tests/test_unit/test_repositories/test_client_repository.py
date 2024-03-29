import uuid
from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exists, select, insert, update, delete, text

import pytest
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.repositories.client import ClientRepository
from sqlalchemy.ext.asyncio import AsyncEngine

from src.data_access.postgresql.errors.client import (
    ClientNotFoundError,
    ClientPostLogoutRedirectUriError,
    ClientRedirectUriError,
    ClientScopesError
)
from src.data_access.postgresql.tables.client import (
    Client,
    ClientClaim,
    ClientRedirectUri,
    ClientSecret,
    ResponseType,
    clients_response_types,
    clients_grant_types,
    clients_scopes,
)
from src.data_access.postgresql.tables import PersistentGrantType, ClientScope


@pytest.mark.asyncio
class TestClientRepository:
    async def test_get_client_by_client_id(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        client = await client_repo.get_client_by_client_id(
            client_id="test_client"
        )
        assert isinstance(client, Client)
        assert client.client_id == "test_client"

    async def test_get_client_by_client_id_not_exists(self, connection: AsyncSession) -> None:
        client_repo_error = ClientRepository(connection)
        with pytest.raises(ClientNotFoundError):
            await client_repo_error.get_client_by_client_id(
                client_id="test_client_not_exist"
            )

    @pytest.mark.parametrize("client_id, boolean",
                             [("test_client", True),
                              ("test_client_not_exist", False)])
    async def test_validate_client_by_client_id(self, connection: AsyncSession,
                                                client_id,
                                                boolean) -> None:
        client_repo = ClientRepository(connection)
        result = await client_repo.validate_client_by_client_id(
            client_id=client_id
        )
        assert result == boolean


    async def test_validate_client_by_int_id(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        result = await client_repo.validate_client_by_int_id(
            client_id=1
        )
        assert result == True

    async def test_validate_client_by_int_id_not_exists(self, connection: AsyncSession) -> None:
        client_repo_error = ClientRepository(connection)
        with pytest.raises(ClientNotFoundError):
            await client_repo_error.validate_client_by_int_id(
                client_id=999
            )

    async def test_get_client_secret_by_client_id(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        expected = "past"
        secret = await client_repo.get_client_secrete_by_client_id(
            client_id="test_client"
        )
        assert secret == expected

    async def test_get_client_secret_by_client_id_not_exists(self, connection: AsyncSession) -> None:
        client_repo_error = ClientRepository(connection)
        with pytest.raises(ClientNotFoundError):
            await client_repo_error.get_client_secrete_by_client_id(
                client_id="test_client_not_exist"
            )

    async def test_validate_post_logout_redirect_uri(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        result = await client_repo.validate_post_logout_redirect_uri(
            client_id="test_client",
            logout_redirect_uri="http://thompson-chung.com/",
        )
        assert result

    async def test_validate_post_logout_redirect_uri_not_exists(self, connection: AsyncSession) -> None:
        client_repo_error = ClientRepository(connection)
        with pytest.raises(ClientPostLogoutRedirectUriError):
            await client_repo_error.validate_post_logout_redirect_uri(
                client_id="test_client",
                logout_redirect_uri="http://redirect-uri-not-exists.com/",
            )

    async def test_validate_client_redirect_uri(self,
                                                connection: AsyncSession,
                                                monkeypatch) -> None:
        mock_get_client_by_client_id = AsyncMock()
        mock_get_client_by_client_id.return_value = AsyncMock(id=1)
        monkeypatch.setattr(ClientRepository,
                            "get_client_by_client_id",
                            mock_get_client_by_client_id)
        client_repo = ClientRepository(connection)
        uri = await client_repo.validate_client_redirect_uri(
            client_id="test_client", redirect_uri="http://127.0.0.1:8888/callback/"
        )
        assert uri is True

    async def test_validate_client_redirect_uri_error(self, connection: AsyncSession, monkeypatch) -> None:
        mock_get_client_by_client_id = AsyncMock()
        mock_get_client_by_client_id.return_value = AsyncMock(id=1)
        monkeypatch.setattr(ClientRepository,
                            "get_client_by_client_id",
                            mock_get_client_by_client_id)
        client_repo = ClientRepository(connection)
        with pytest.raises(ClientRedirectUriError):
            await client_repo.validate_client_redirect_uri(
                client_id="test_client", redirect_uri="just_uri"
            )

    async def test_get_client_scopes(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        scopes = await client_repo.get_client_scopes(
            client_id=1
        )
        assert isinstance(scopes, list)
        assert isinstance(scopes[0], str)
        assert "openid" in scopes[0]

    async def test_get_client_scopes_not_exists(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(Exception):
            await client_repo.get_client_scopes(client_id=999)

    async def test_get_client_redirect_uris(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        result = await client_repo.get_client_redirect_uris(client_id=1)

        assert isinstance(result, list)
        assert all(isinstance(uri, str) for uri in result)
        assert len(result) > 0

    async def test_get_client_redirect_uris_not_exists(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        result = await client_repo.get_client_redirect_uris(client_id=999)

        assert isinstance(result, list)
        assert len(result) == 0

    async def test_get_client_claims(self, connection: AsyncSession) -> None:
        
        
        params = {"type": "",
                    "value": "",
                    "client_id": 1}
        await connection.execute(insert(ClientClaim).values(**params))
        await connection.commit()

        client_repo = ClientRepository(connection)
        result = await client_repo.get_client_claims(client_id=1)

        assert isinstance(result, list)
        assert all(isinstance(uri, str) for uri in result)
        assert len(result) > 0

    async def test_get_client_claims_not_exists(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        result = await client_repo.get_client_claims(client_id=999)

        assert isinstance(result, list)
        assert len(result) == 0

    async def test_create(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
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
        client = await connection.execute(
            select(Client).where(Client.client_id == "registration_test_client")
        )

        client = client.scalar_one_or_none()

        assert client is not None
        assert client.client_id == "registration_test_client"
        assert client.client_name == "regtestent"
        assert client.client_uri == "http://regtestent.com/"


    async def test_create_with_incorrect_parameters(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
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


    async def test_add_secret(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

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

        
        
        result = await connection.execute(insert(Client).values(**new_client).returning(Client.id))
        client_id_int = result.scalar_one()

        await connection.commit()

        await client_repo.add_secret(client_id_int=client_id_int, value="test_secret")

        
        secret = await connection.execute(
            select(ClientSecret).where(ClientSecret.client_id == client_id_int)
        )
        secret = secret.scalar_one_or_none()

        assert secret is not None
        assert secret.client_id == client_id_int
        assert secret.value == "test_secret"

    async def test_add_secret_incorrect_parameters(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(Exception):
            await client_repo.add_secret(client_id_int=99, value="secret_test_secret")

    async def test_add_scope(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

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

        result = await connection.execute(insert(Client).values(**new_client).returning(Client.id))
        client_id_int = result.scalar_one()
        await connection.commit()
        scope_ids:dict={}
        scope_ids['resource_id'] = 1
        scope_ids['scope_id'] = 1
        scope_ids['claim_id'] = 1

        await client_repo.add_scope(client_id_int=client_id_int, scope_ids=scope_ids)

        scope = await client_repo.get_client_scopes(client_id_int)
        assert len(scope) == 1 

    async def test_add_scope_incorrect_parameters(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(Exception):
            await client_repo.add_scope(client_id_int=99, scope="test_scope")


    async def test_add_redirect_uris(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

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

        result = await connection.execute(insert(Client).values(**new_client).returning(Client.id))
        client_id_int = result.scalar_one()
        await connection.commit()

        insert_redirect_uris = ["https://www.google.com/", "https://www.facebook.com/"]
        await client_repo.add_redirect_uris(client_id_int=client_id_int,
                                            redirect_uris=insert_redirect_uris)

        
        uris_object = await connection.scalars(
            select(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
        )
        res_redirect_uris = [uri_obj.redirect_uri for uri_obj in uris_object.all()]

        assert res_redirect_uris is not None
        assert res_redirect_uris == insert_redirect_uris

    async def test_add_redirect_uris_incorrect_parameters(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(Exception):
            await client_repo.add_redirect_uris(client_id_int=99,
                                                redirect_uris=["https://www.google.com/"])

    async def test_get_access_token_type_id(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        result = await client_repo.get_access_token_type_id(str_type="jwt")
        id = 1
        assert isinstance(result, int)
        assert result == id

    async def test_get_access_token_type_id_not_exist(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(ValueError):
            await client_repo.get_access_token_type_id(str_type="not_exist")

    async def test_get_refresh_token_usage_type_id(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        result = await client_repo.get_refresh_token_usage_type_id(str_type="one_time_only")
        id = 1
        assert isinstance(result, int)
        assert result == id

    async def test_get_refresh_token_usage_type_id_not_exist(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(ValueError):
            await client_repo.get_refresh_token_usage_type_id(str_type="not_exist")

    async def test_get_refresh_token_expiration_type_id(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        result = await client_repo.get_refresh_token_expiration_type_id(str_type="absolute")
        id = 1
        assert isinstance(result, int)
        assert result == id

    async def test_get_refresh_token_expiration_type_id_not_exist(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(ValueError):
            await client_repo.get_refresh_token_expiration_type_id(str_type="not_exist")

    async def test_update(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

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

        
        
        await connection.execute(insert(Client).values(**new_client).returning(Client.id))
        await connection.commit()

        new_params = {
            "client_name": "regtestent_new",
            "client_uri": "https://regtestent-new.com/",
        }
        await client_repo.update(client_id=unique_client_id, **new_params)

        client_result = await connection.scalars(
            select(Client).where(Client.client_id == unique_client_id)
        )
        client = client_result.first()

        assert client is not None
        assert isinstance(client, Client)
        assert client.client_name == "regtestent_new"
        assert client.client_uri == "https://regtestent-new.com/"

    async def test_update_non_existent_client_id(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

        non_existent_client_id = "non_existent_client_id"
        update_data = {"client_name": "updated_client_name"}

        await client_repo.update(non_existent_client_id, **update_data)
        client = await connection.execute(
            select(Client).where(Client.client_id == non_existent_client_id)
        )
        client = client.scalar_one_or_none()

        assert client is None

    async def test_delete_scope(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

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

        result = await connection.execute(insert(Client).values(**new_client).returning(Client.id))
        client_id_int = result.scalar_one()
        scope_ids:dict={}
        scope_ids['resource_id'] = 1
        scope_ids['scope_id'] = 1
        scope_ids['claim_id'] = 1
        
        await client_repo.add_scope(client_id_int=client_id_int, scope_ids=scope_ids,)
        await connection.commit()
    
        await client_repo.delete_scope(client_id_int=client_id_int)
        await client_repo.session.commit()
        with pytest.raises(ClientScopesError):
            await client_repo.get_client_scopes(client_id_int)
        client =(await client_repo.session.execute(select(Client).where(Client.id == client_id_int))).first()[0]
        assert client.scope == []


    async def test_delete_redirect_uris(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

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

        result = await connection.execute(insert(Client).values(**new_client).returning(Client.id))
        client_id_int = result.scalar_one()
        await connection.execute(insert(ClientRedirectUri).values(
            client_id=client_id_int,
            redirect_uri="https://www.google.com/",
        ))
        await connection.commit()

    
        redirect_uri = await connection.execute(
            select(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
        )
        redirect_uri = redirect_uri.scalar_one_or_none()

        assert redirect_uri is not None

        await client_repo.delete_redirect_uris(client_id_int=client_id_int)
        redirect_uri = await connection.execute(
            select(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
        )
        redirect_uri = redirect_uri.scalar_one_or_none()

        assert redirect_uri is None


    async def test_delete_client_by_client_id(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

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

        await connection.execute(insert(Client).values(**new_client))
        await connection.commit()
        client = await connection.execute(
            select(Client).where(Client.client_id == unique_client_id)
        )
        client = client.scalar_one_or_none()

        assert client is not None

        await client_repo.delete_client_by_client_id(client_id=unique_client_id)
        client = await connection.execute(
            select(Client).where(Client.client_id == unique_client_id)
        )
        client = client.scalar_one_or_none()

        assert client is None

    async def test_get_all(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        clients = await connection.execute(select(Client))
        repo_clients_lst = [client[0] for client in clients.all()]

        function_clients_lst = await client_repo.get_all()

        assert isinstance(repo_clients_lst, list)
        assert repo_clients_lst == function_clients_lst


    async def test_add_response_type(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

        await client_repo.add_response_type(client_id_int=1, response_type="code")
        query = select(
            clients_response_types.c.client_id,
            clients_response_types.c.response_type_id
        ).select_from(
            clients_response_types
            .join(Client, Client.id == clients_response_types.c.client_id)
            .join(ResponseType, ResponseType.id == clients_response_types.c.response_type_id)
        ).where(clients_response_types.c.client_id == 1)

        result = await connection.execute(query)
        row = result.fetchone()

        assert row is not None
        assert row.client_id == 1
        assert row.response_type_id == 1


    async def test_add_response_type_for_non_existent_client(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(Exception):
            await client_repo.add_response_type(client_id_int=99, response_type="code")

    async def test_add_response_type_for_non_existent_response_type(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(Exception):
            await client_repo.add_response_type(client_id_int=1, response_type="non_existent_response_type")

    async def test_add_grant_type(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)

        await client_repo.add_grant_type(client_id_int=1, grant_type="authorization_code")
        query = select(
            clients_grant_types.c.client_id,
            clients_grant_types.c.persistent_grant_type_id
        ).select_from(
            clients_grant_types
            .join(Client, Client.id == clients_grant_types.c.client_id)
            .join(PersistentGrantType, PersistentGrantType.id == clients_grant_types.c.persistent_grant_type_id)
        ).where(clients_grant_types.c.client_id == 1)

        result = await connection.execute(query)
        row = result.fetchone()

        assert row is not None
        assert row.client_id == 1
        assert row.persistent_grant_type_id == 1

    async def test_add_grant_type_for_non_existent_client(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(Exception):
            await client_repo.add_grant_type(client_id_int=99, grant_type="authorization_code")

    async def test_add_grant_type_for_non_existent_grant_type(self, connection: AsyncSession) -> None:
        client_repo = ClientRepository(connection)
        with pytest.raises(Exception):
            await client_repo.add_grant_type(client_id_int=1, grant_type="non_existent_grant_type")

    async def test_delete_clients_response_types(self, connection: AsyncSession) -> None:
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

        result = await connection.execute(insert(Client).values(**new_client).returning(Client.id))
        client_id_int = result.scalar_one()
        await connection.execute(
            insert(clients_response_types).values(
                client_id=client_id_int,
                response_type_id=1
            )
        )
        await connection.commit()

    
        clients_resp_type = await connection.scalars(
            select(clients_response_types).where(clients_response_types.c.client_id == client_id_int)
        )
        clients_resp_type = clients_resp_type.one_or_none()

        assert clients_resp_type is not None

        client_repo = ClientRepository(connection)

        await client_repo.delete_clients_response_types(client_id_int=client_id_int)
    
        clients_resp_type = await connection.scalars(
            select(clients_response_types).where(clients_response_types.c.client_id == client_id_int)
        )
        clients_resp_type = clients_resp_type.one_or_none()

        assert clients_resp_type is None

    async def test_delete_clients_grant_types(self, connection: AsyncSession) -> None:
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

        result = await connection.execute(insert(Client).values(**new_client).returning(Client.id))
        client_id_int = result.scalar_one()
        await connection.execute(
            insert(clients_grant_types).values(
                client_id=client_id_int,
                persistent_grant_type_id=1
            )
        )
        await connection.commit()

    
        clients_grant_type = await connection.scalars(
            select(clients_grant_types).where(clients_grant_types.c.client_id == client_id_int)
        )
        clients_grant_type = clients_grant_type.one_or_none()

        assert clients_grant_type is not None

        client_repo = ClientRepository(connection)

        await client_repo.delete_clients_grant_types(client_id_int=client_id_int)

        clients_grant_type = await connection.scalars(
            select(clients_grant_types).where(clients_grant_types.c.client_id == client_id_int)
        )
        clients_grant_type = clients_grant_type.one_or_none()

        assert clients_grant_type is None





































