from sqlalchemy import exists, select
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
)


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

    def __repr__(self) -> str:
        return "Client Repository"
