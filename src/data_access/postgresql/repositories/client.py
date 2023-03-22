from sqlalchemy import exists, select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
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
    ClientScope,
    ClientSecret,
    AccessTokenType,
    RefreshTokenExpirationType,
    RefreshTokenUsageType,
)
from typing import Optional, Any, Union
from src.presentation.api.models.registration import ClientRequestModel, ClientUpdateRequestModel
from src.data_access.postgresql.errors import DuplicationError
import time

class ClientRepository(BaseRepository):
    async def get_client_by_client_id(self, client_id: str) -> Client:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            client = await session.execute(
                select(Client).where(Client.client_id == client_id)
            )

            client = client.first()
            if client is None:
                raise ClientNotFoundError(
                    "Client you are looking for does not exist"
                )
            return client[0]

    async def validate_client_by_client_id(self, client_id: str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(
                    exists().where(
                        Client.client_id == client_id,
                    )
                )
            )
            result = result.first()
            if not result[0]:
                raise ClientNotFoundError(
                    "Client you are looking for does not exist"
                )
            return result[0]

    async def validate_client_by_int_id(self, client_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
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
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            secrete = await session.execute(
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
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            logout_redirect_uri_obj = await session.execute(
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
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            client_id_int = (
                await self.get_client_by_client_id(client_id=client_id)
            ).id
            redirect_uri_obj = await session.execute(
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

    async def get_client_scopes(self, client_id: int) -> str:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            scopes = await session.execute(
                select(ClientScope).where(ClientScope.client_id == client_id)
            )
            return scopes.first()[-1].scope

    async def get_client_redirect_uris(self, client_id: int) -> list[str]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            uris = await session.execute(
                select(ClientRedirectUri)
                .join(Client, ClientSecret.client_id == Client.id)
                .where(Client.client_id == client_id)
            )

            result = []
            for uri in uris:
                result.append(uri[0].redirect_uri)

            return result

    async def get_client_claims(self, client_id: int) -> list[str]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            uris = await session.execute(
                select(ClientClaim).where(ClientClaim.client_id == client_id)
            )

            result = []
            for uri in uris:
                result.append(uri[0].type + ":" + uri[0].value)

            return result

    async def create(
        self, 
        params:dict[str:Any],
    ) -> None:
        try:
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess

                await session.execute(insert(Client).values(**params))
                await session.commit()
        except:
            raise DuplicationError
    
    async def add_secret(
        self, 
        client_id_int:int,
        value:str,
        secret_type:str = "random",
        expiration_in_seconds:int = 30*24*60*60,
        description = "Randomly generated by server"
    ) -> None:
        try:
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess
                await session.execute(insert(ClientSecret).values(
                    client_id = client_id_int,
                    expiration = int(time.time() + expiration_in_seconds),
                    value = value,
                    type = secret_type,
                    description = description
                    )
                )
                await session.commit()
        except:
            raise DuplicationError
        
    async def add_scope(
        self, 
        client_id_int:int,
        scope:str,
    ) -> None:
        try:
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess
                await session.execute(insert(ClientScope).values(
                    client_id = client_id_int,
                    scope = scope,
                    )
                )
                await session.commit()
        except:
            raise DuplicationError

    async def add_redirect_uris(
        self, 
        client_id_int:int,
        redirect_uris:list[str],
    ) -> None:
        try:
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess
                for uri in redirect_uris:
                    await session.execute(insert(ClientRedirectUri).values(
                        client_id = client_id_int,
                        redirect_uri = uri,
                        )
                    )
                    await session.commit()
        except:
            raise DuplicationError

    async def get_access_token_type_id(self, str_type):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            result = await session.execute(
                select(AccessTokenType)
                .where(AccessTokenType.type == str_type)
            )
            result = result.first()

            if result is None:
                ValueError
            return result[0].id
    
    async def get_refresh_token_usage_type_id(self, str_type):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            result = await session.execute(
                select(RefreshTokenUsageType)
                .where(RefreshTokenUsageType.type == str_type)
            )
            result = result.first()

            if result is None:
                ValueError
            return result[0].id

    async def get_refresh_token_expiration_type_id(self, str_type):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            result = await session.execute(
                select(RefreshTokenExpirationType)
                .where(RefreshTokenExpirationType.type == str_type)
            )
            result = result.first()

            if result is None:
                ValueError
            return result[0].id
    
    async def update(self, client_id, **kwargs):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            updates = (
                        update(Client)
                        .values(**kwargs)
                        .where(Client.client_id == client_id)
                    )
            await session.execute(updates)
            await session.commit()


    async def delete_scope(
        self, 
        client_id_int:int,
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            await session.execute(
                delete(ClientScope).where(ClientScope.client_id == client_id_int)
            )
            await session.commit()

    async def delete_redirect_uris(
        self, 
        client_id_int:int,
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            await session.execute(
                delete(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id_int)
            )
            await session.commit()


    def __repr__(self) -> str:
        return "Client Repository"

