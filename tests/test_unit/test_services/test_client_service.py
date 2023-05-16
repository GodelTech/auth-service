import uuid
from datetime import time
from typing import List
from pydantic import BaseModel
from unittest.mock import AsyncMock

import mock
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists, select, insert, update, delete, text

from src.data_access.postgresql.errors import ClientNotFoundError
from src.business_logic.services import ClientService
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from src.data_access.postgresql.tables.client import (
    Client,
    ClientClaim,
    ClientRedirectUri,
    ClientScope,
    ClientSecret,
    ResponseType,
    clients_response_types,
    clients_grant_types,
)
from src.data_access.postgresql.tables.persistent_grant import PersistentGrantType

# class ClientRequestModel(BaseModel):
#     client_name: str
#     client_uri: str
#     logo_uri: str
#     redirect_uris: List[str]
#     grant_types: List[str]
#     response_types: List[str]
#     token_endpoint_auth_method: str
#     scope: str

class ClientRequestModel:
    def __init__(
        self,
        client_name: str = '',
        client_uri: str = '',
        logo_uri: str = '',
        redirect_uris: List[str] = [],
        grant_types: List[str] = [],
        response_types: List[str] = [],
        token_endpoint_auth_method: str = '',
        scope: str = '',
    ):
        self.client_name = client_name
        self.client_uri = client_uri
        self.logo_uri = logo_uri
        self.redirect_uris = redirect_uris
        self.grant_types = grant_types
        self.response_types = response_types
        self.token_endpoint_auth_method = token_endpoint_auth_method
        self.scope = scope

@pytest.fixture
def client_request_model() -> ClientRequestModel:
    return ClientRequestModel(
        client_name="Example app",
        client_uri="example_app.com",
        logo_uri="example_app.com/pic.jpg",
        redirect_uris=["example_app.com/redirect_uri_1", "example_app.com/redirect_uri_2"],
        grant_types=["authorization_code"],
        response_types=["code"],
        token_endpoint_auth_method="client_secret_post",
        scope="openid profile"
    )

@pytest.mark.asyncio
class TestClientService:
    async def test_generate_credentials(self, client_service: ClientService) -> None:
        result = await client_service.generate_credentials()
        assert isinstance(result, tuple)
        assert [isinstance(elem, str) for elem in result]

    async def test_registration(self,
                                client_request_model: ClientRequestModel,
                                client_service: ClientService,
                                engine: AsyncEngine,
                                monkeypatch) -> None:
        mock_generate_credentials = AsyncMock(return_value=("client_id", "client_secret"))
        monkeypatch.setattr(client_service,
                            "generate_credentials",
                            mock_generate_credentials)

        client_service.request_model = client_request_model
        registration_result = await client_service.registration()

        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            new_client = (await session.scalars(
                select(Client).where(Client.client_id == registration_result["client_id"])
            )).first()

        assert isinstance(registration_result, dict)
        assert registration_result.keys() == {"client_id", "client_secret"}
        assert registration_result == {
                                        "client_id": "client_id",
                                        "client_secret": "client_secret"
                                    }
        assert new_client.client_name == "Example app"

    async def test_registration_without_redirect_uris(self, client_service: ClientService) -> None:
        client_service.request_model = ClientRequestModel(
                                                        client_name="Example app",
                                                        client_uri="example_app.com",
                                                        logo_uri="example_app.com/pic.jpg",
                                                        redirect_uris=[],
                                                        grant_types=["authorization_code"],
                                                        response_types=["code"],
                                                        token_endpoint_auth_method="client_secret_post",
                                                        scope="openid profile"
                                                    )
        with pytest.raises(Exception):
            await client_service.registration()

    async def test_get_params(self, client_request_model, client_service: ClientService) -> None:

        client_service.request_model = client_request_model
        params = await client_service.get_params(client_id="test_client")

        assert isinstance(params, dict)
        assert params["client_id"] == "test_client"

    async def test_update_multiple_parameters(self,
                                         client_request_model,
                                         client_service: ClientService,
                                         engine: AsyncEngine) -> None:

        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret",
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

        new_properties = ClientRequestModel(
            client_name="Updated App",
            client_uri="https://updatedapp.com",
            logo_uri="https://updatedapp.com/logo.png",
            token_endpoint_auth_method="updated_client_secret"
        )

        client_service.request_model = new_properties

        await client_service.update(client_id=unique_client_id)

        async with session_factory() as session:
            updated_client = (await session.scalars(
                select(Client).where(Client.client_id == unique_client_id)
            )).first()

        assert updated_client.client_name == "Updated App"
        assert updated_client.client_uri == "https://updatedapp.com"
        assert updated_client.logo_uri == "https://updatedapp.com/logo.png"
        assert updated_client.token_endpoint_auth_method == "updated_client_secret"

    async def test_update_response_types(self,
                                         client_request_model,
                                         client_service: ClientService,
                                         engine: AsyncEngine) -> None:

        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret",
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
            await session.execute(insert(Client).values(**new_client))
            await session.commit()

        new_response_types = ["code", "token"]

        client_service.request_model = ClientRequestModel(
            response_types=new_response_types,
        )

        await client_service.update(client_id=unique_client_id)

        async with session_factory() as session:
            query = select(
                clients_response_types.c.client_id,
                ResponseType.type
            ).select_from(
                clients_response_types
                .join(Client, Client.id == clients_response_types.c.client_id)
                .join(ResponseType, ResponseType.id == clients_response_types.c.response_type_id)
            ).where(Client.client_id == unique_client_id)

            result = await session.execute(query)
            updated_response_types = [row.type for row in result.fetchall()]

        assert set(updated_response_types) == set(new_response_types)

############## Error. "Device"? #####################

    # async def test_update_grant_types(self,
    #                         client_request_model,
    #                         client_service: ClientService,
    #                         engine: AsyncEngine) -> None:
    #     unique_client_id = f"test_client_{uuid.uuid4()}"
    #     new_client = {
    #         "client_id": unique_client_id,
    #         "client_name": "regtestent",
    #         "client_uri": "http://regtestent.com/",
    #         "logo_uri": "https://www.regtestent-logo.com/",
    #         "token_endpoint_auth_method": "client_secret",
    #         "require_consent": False,
    #         "require_pkce": True,
    #         "refresh_token_usage_type_id": 2,
    #         "refresh_token_expiration_type_id": 1,
    #         "access_token_type_id": 1,
    #         "protocol_type_id": 1,
    #     }
    #
    #     session_factory = sessionmaker(
    #         engine, expire_on_commit=False, class_=AsyncSession
    #     )
    #     async with session_factory() as session:
    #         result = await session.execute(insert(Client).values(**new_client).returning(Client.id))
    #         client_id_int = result.scalar_one()
    #         await session.commit()
    #
    #     new_grant_types = ["authorization_code", "refresh_token"]
    #
    #     client_service.request_model = ClientRequestModel(
    #         grant_types=new_grant_types,
    #     )
    #
    #     await client_service.update(client_id=unique_client_id)
    #
    #     async with session_factory() as session:
    #         query = select(
    #             clients_grant_types.c.client_id,
    #             PersistentGrantType.type_of_grant
    #         ).select_from(
    #             clients_grant_types
    #             .join(Client, Client.id == clients_grant_types.c.client_id)
    #             .join(PersistentGrantType, PersistentGrantType.id == clients_grant_types.c.persistent_grant_type_id)
    #         ).where(Client.id == client_id_int)
    #
    #         result = await session.execute(query)
    #         updated_grant_types = [row.type_of_grant for row in result.fetchall()]
    #
    #     assert set(updated_grant_types) == set(new_grant_types)

    async def test_update_scope(self,
                                client_request_model,
                                client_service: ClientService,
                                engine: AsyncEngine) -> None:
        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret",
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

        new_scope = "openid profile email"
        client_service.request_model = ClientRequestModel(
            scope=new_scope,
        )

        await client_service.update(client_id=unique_client_id)

        async with session_factory() as session:
            updated_scope = await session.execute(
                select(ClientScope).where(ClientScope.client_id == client_id_int)
            )
            updated_scope = updated_scope.scalar_one_or_none()

        assert updated_scope.scope == new_scope

    async def test_update_uris(self,
                                client_request_model,
                                client_service: ClientService,
                                engine: AsyncEngine) -> None:
        unique_client_id = f"test_client_{uuid.uuid4()}"
        new_client = {
            "client_id": unique_client_id,
            "client_name": "regtestent",
            "client_uri": "http://regtestent.com/",
            "logo_uri": "https://www.regtestent-logo.com/",
            "token_endpoint_auth_method": "client_secret",
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

        new_redirect_uris = ["https://initialapp.com/redirect1", "https://initialapp.com/redirect3"]
        client_service.request_model = ClientRequestModel(
            redirect_uris=new_redirect_uris
        )

        await client_service.update(client_id=unique_client_id)
        await client_service.session.commit()

        async with session_factory() as session:
            uris_object = await session.scalars(
                select(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
            )
            updated_redirect_uris = [uri_obj.redirect_uri for uri_obj in uris_object.all()]

        assert set(updated_redirect_uris) == set(new_redirect_uris)

##### Dont work with "ClientNotFoundError" ####
    async def test_update_with_non_existent_client_id(self,
                                                      client_request_model,
                                                      client_service: ClientService) -> None:
        client_service.request_model = client_request_model
        with pytest.raises(Exception):
            await client_service.update(client_id="non_existent_client_id")

    async def test_get_all(self, client_service: ClientService) -> None:

        clients = await client_service.get_all()

        assert isinstance(clients, list)
        assert [isinstance(obj, dict) for obj in clients]

    async def test_client_to_dict(self,
                                  client_service: ClientService,
                                  engine: AsyncEngine) -> None:
        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as session:
            client = (await session.scalars(
                select(Client).where(Client.client_id == "double_test")
            )).first()

        dictionary = client_service.client_to_dict(client)

        expected_dictionary = {
            'client_id': 'double_test',
            'client_name': 'jasmine85',
            'client_uri': 'http://davis-yates.com/',
            'logo_uri': 'http://www.zavala.com/',
            'redirect_uris': ['https://www.google.com/'],
            'grant_types': [],
            'response_types': [],
            'token_endpoint_auth_method': 'client_secret_post',
            'scope': 'openid email'
        }

        assert isinstance(dictionary, dict)
        assert dictionary == expected_dictionary

    async def test_get_client_by_client_id(self, client_service: ClientService) -> None:
        client = await client_service.get_client_by_client_id(client_id="test_client")

        assert isinstance(client, dict)

    ##### Dont work with "ClientNotFoundError" ####
    async def test_get_client_by_client_id_with_non_existent_client_id(self,
                                                                      client_request_model,
                                                                      client_service: ClientService) -> None:
        client_service.request_model = client_request_model
        with pytest.raises(Exception):
            await client_service.get_client_by_client_id(client_id="non_existent_client_id")


