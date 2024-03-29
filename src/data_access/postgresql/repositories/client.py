from typing import List
from sqlalchemy import exists, select, insert, update, delete, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine

from src.data_access.postgresql.errors.client import (
    ClientNotFoundError,
    ClientPostLogoutRedirectUriError,
    ClientRedirectUriError,
)
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.client import (
    Client,
    ClientClaim,
    ClientPostLogoutRedirectUri,
    ClientRedirectUri,
    ClientSecret,
    AccessTokenType,
    RefreshTokenExpirationType,
    RefreshTokenUsageType,
    ResponseType,
    clients_response_types,
    clients_grant_types,
    clients_scopes,
)
from src.data_access.postgresql.tables import PersistentGrantType, ClientScope
from typing import Optional, Any, Union
from src.presentation.api.models.registration import ClientRequestModel, ClientUpdateRequestModel
from src.data_access.postgresql.errors import DuplicationError, ClientScopesError
import time

class ClientRepository(BaseRepository):

    async def get_client_by_client_id(self, client_id: str) -> Client:
        client = await self.session.execute(
            select(Client).where(Client.client_id == client_id)
        )

        client = client.first()
        if client is None:
            raise ClientNotFoundError(
                "Client you are looking for does not exist"
            )
        return client[0]

    async def validate_client_by_client_id(self, client_id: str) -> bool:
        result = await self.session.execute(
            select(
                exists().where(
                    Client.client_id == client_id,
                )
            )
        )
        result = result.first()
        if not result[0]:
            return False
        else:
            return True

    async def validate_client_by_int_id(self, client_id: int) -> bool:
        result = await self.session.execute(
            select(
                exists().where(
                    Client.id == client_id,
                )
            )
        )
        result = result.first()
        if not result[0]:
            raise ClientNotFoundError(
                "Client you are looking for does not exist"
            )
        return result[0]

    async def get_client_secrete_by_client_id(self, client_id: str) -> str:
        secrete = await self.session.execute(
            select(ClientSecret)
            .join(Client, ClientSecret.client_id == Client.id)
            .where(Client.client_id == client_id)
        )
        secrete = secrete.first()

        if secrete is None:
            raise ClientNotFoundError(
                "Client you are looking for does not exist"
            )
        return secrete[0].value

    async def validate_post_logout_redirect_uri(
        self, client_id: str, logout_redirect_uri: str
    ) -> bool:
        logout_redirect_uri_obj = await self.session.execute(
            select(ClientPostLogoutRedirectUri)
            .join(
                Client, ClientPostLogoutRedirectUri.client_id == Client.id
            )
            .where(
                Client.client_id == client_id,
                ClientPostLogoutRedirectUri.post_logout_redirect_uri
                == logout_redirect_uri,
            )
        )

        result = logout_redirect_uri_obj.first()
        if not result:
            raise ClientPostLogoutRedirectUriError(
                "Post logout redirect uri you are looking for does not exist"
            )
        return True

    async def validate_client_redirect_uri(
        self, client_id: str, redirect_uri: str
    ) -> bool:
        client_id_int = (
            await self.get_client_by_client_id(client_id=client_id)
        ).id
        redirect_uri_obj = await self.session.execute(
            select(ClientRedirectUri).where(
                ClientRedirectUri.client_id == client_id_int,
                ClientRedirectUri.redirect_uri == redirect_uri,
            )
        )

        result = redirect_uri_obj.first()
        if not result:
            raise ClientRedirectUriError(
                "Redirect uri you are looking for does not exist"
            )
        else:
            return True

    async def get_client_scopes(self, client_id: int) -> list[str]:
        client = (await self.session.execute(
            select(Client).where(Client.id == client_id)
        )).first()
        scopes = client[0].scope
        result = [f'{scope.resource.name}:{scope.scope.name}:{scope.claim}'for scope in scopes]
        if len(result) == 0:
            raise ClientScopesError
        return result

    async def get_client_redirect_uris(self, client_id: int) -> list[str]:
        uris = await self.session.execute(
            select(ClientRedirectUri)
            .join(Client, ClientRedirectUri.client_id == Client.id)
            .where(Client.id == client_id)
        )
        result = []
        for uri in uris:
            result.append(uri[0].redirect_uri)

        return result

    async def get_client_claims(self, client_id: int) -> list[str]:
        uris = await self.session.execute(
            select(ClientClaim).where(ClientClaim.client_id == client_id)
        )

        result = []
        for uri in uris:
            result.append(uri[0].type + ":" + uri[0].value)

        return result

    async def list_all_redirect_uris_by_client(
        self, client_id: str
    ) -> list[str]:
        result = await self.session.scalars(
            select(ClientRedirectUri.redirect_uri)
            .join(Client, ClientRedirectUri.client_id == Client.id)
            .where(Client.client_id == client_id)
        )
        return result.all()

    async def list_all_scopes_by_client(self, client_id: str) -> List[str]:
        client = await self.get_client_by_client_id(client_id)
        result = []
        for scope in client.scope:
            if scope.scope.name == 'userinfo':
                result.append(str(scope.claim))
            else:
                result.append(f'{scope.resource.name}:{scope.scope.name}:{scope.claim}')
        return result

    async def exists(self, client_id: str) -> bool:
        result = await self.session.execute(
            select(Client)
            .where(Client.client_id == client_id)
            .exists()
            .select()
        )
        return result.scalar()

    async def get_auth_code_lifetime_by_client(self, client_id: str) -> int:
        result = await self.session.execute(
            select(Client.authorization_code_lifetime).where(
                Client.client_id == client_id
            )
        )
        return result.scalar()

    async def get_device_code_lifetime_by_client(self, client_id: str) -> int:
        result = await self.session.execute(
            select(Client.device_code_lifetime).where(
                Client.client_id == client_id
            )
        )
        return result.scalar()

    async def create(
        self, 
        params: dict[str:Any],
    ) -> None:
        #try:
            await self.session.execute(insert(Client).values(**params))
        # except:
        #     raise DuplicationError
    
    async def add_secret(
        self, 
        client_id_int:int,
        value:str,
        secret_type:str = "random",
        expiration_in_seconds:int = 30*24*60*60,
        description = "Randomly generated by server"
    ) -> None:
        try:
            await self.session.execute(insert(ClientSecret).values(
                client_id = client_id_int,
                expiration = int(time.time() + expiration_in_seconds),
                value = value,
                type = secret_type,
                description = description
                )
            )
        except:
            raise DuplicationError
        
    async def add_scope(
        self, 
        client_id_int:int,
        scope_ids:str,
    ) -> None:
        scope_id = (await self.session.execute(
            select(ClientScope).where(
                ClientScope.resource_id == scope_ids['resource_id'], 
                ClientScope.scope_id == scope_ids['scope_id'],
                ClientScope.claim_id == scope_ids['claim_id']
            )
        )).first()
        if scope_id is None:
            raise ClientScopesError

        scope_id = scope_id[0].id
        await self.session.execute(insert(clients_scopes).values(
            client_id = client_id_int,
            scope_id = scope_id,
            )
        )
        

    async def add_redirect_uris(
        self, 
        client_id_int:int,
        redirect_uris:list[str],
    ) -> None:
        try:
            
            for uri in redirect_uris:
                await self.session.execute(insert(ClientRedirectUri).values(
                    client_id = client_id_int,
                    redirect_uri = uri,
                    )
                )
        except:
            raise DuplicationError

    async def get_access_token_type_id(self, str_type):
            result = await self.session.execute(
                select(AccessTokenType)
                .where(AccessTokenType.type == str_type)
            )
            result = result.first()

            if result is None:
                raise ValueError
            return result[0].id
    
    async def get_refresh_token_usage_type_id(self, str_type):
            result = await self.session.execute(
                select(RefreshTokenUsageType)
                .where(RefreshTokenUsageType.type == str_type)
            )
            result = result.first()

            if result is None:
                raise ValueError
            return result[0].id

    async def get_refresh_token_expiration_type_id(self, str_type):
            result = await self.session.execute(
                select(RefreshTokenExpirationType)
                .where(RefreshTokenExpirationType.type == str_type)
            )
            result = result.first()

            if result is None:
                raise ValueError
            return result[0].id

    async def update(self, client_id, **kwargs):
            updates = (
                        update(Client)
                        .values(**kwargs)
                        .where(Client.client_id == client_id)
                    )
            await self.session.execute(updates)

    async def delete_scope(
        self, 
        client_id_int:int,
    ) -> None:
        sql = f'DELETE FROM clients_scopes WHERE client_id={client_id_int}'
        await self.session.execute(text(sql))
    
    async def delete_redirect_uris(
        self, 
        client_id_int:int,
    ) -> None:
        await self.session.execute(
            delete(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
        )
        
    async def delete_client_by_client_id(
        self, 
        client_id:str,
    ) -> None:
        
            await self.session.execute(
                delete(Client)
                .where(Client.client_id == client_id)
            )

    async def get_all(self) -> list[Client]:
            result = await self.session.execute(
                    select(Client)
                )
            result = result.all()
            return [client[0] for client in result]

    async def add_response_type(self, client_id_int, response_type):
        
            response_type_id = (await self.session.execute(
                        select(ResponseType.id).where(
                            ResponseType.type == response_type
                        )
                    )).first()[0]
            await self.session.execute(
                        insert(clients_response_types).values(
                            client_id=client_id_int, 
                            response_type_id=response_type_id
                        )
                    )

    async def add_grant_type(self, client_id_int, grant_type):
        
            grant_type_id = (await self.session.execute(
                        select(PersistentGrantType.id).where(
                            PersistentGrantType.type_of_grant == grant_type
                        )
                    )).first()[0]
            await self.session.execute(
                        insert(clients_grant_types).values(
                            client_id=client_id_int, 
                            persistent_grant_type_id=grant_type_id
                        )
                    )

    async def delete_clients_response_types(self, client_id_int):
        
            sql = f"DELETE FROM clients_response_types WHERE client_id = {client_id_int}"
            await self.session.execute(text(sql))
    
    async def delete_clients_grant_types(self, client_id_int):
        
            sql = f"DELETE FROM clients_grant_types WHERE client_id = {client_id_int}"
            await self.session.execute(text(sql))
    
    async def exists_client_with_provided_client_secret(self, client_id: str, client_secret: str) -> bool:
        query = (select(Client).join(ClientSecret, Client.id == ClientSecret.client_id)
                .where(Client.client_id == client_id, ClientSecret.value == client_secret)
                .exists().select())
        result = await self.session.execute(query)
        return result.scalar()

    def __repr__(self) -> str:
        return "Client Repository"

