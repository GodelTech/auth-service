from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors.client import (
    ClientNotFoundError,
    ClientPostLogoutRedirectUriError,
    ClientRedirectUriError
)
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.client import (
    Client,
    ClientClaim,
    ClientScope,
    ClientPostLogoutRedirectUri,
    ClientSecret,
    ClientRedirectUri
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

    async def validate_client_by_client_id(self, client_id:str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(
                    [
                        exists().where(
                            Client.client_id == client_id,
                        )
                    ]
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
                select(ClientSecret.value).where(ClientSecret.client_id == client_id)
            )
            secrete = secrete.first()

            if secrete is None:
                raise ClientNotFoundError(
                    "Client you are looking for does not exist"
                )
            return secrete[0]

    async def validate_post_logout_redirect_uri(self, client_id: str, logout_redirect_uri: str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            logout_redirect_uri = await session.execute(
                select(
                    [
                        exists().where(
                            ClientPostLogoutRedirectUri.client_id == client_id,
                            ClientPostLogoutRedirectUri.post_logout_redirect_uri == logout_redirect_uri,
                        )
                    ]
                )
            )
            result = logout_redirect_uri.first()
            if not result[0]:
                raise ClientPostLogoutRedirectUriError("Post logout redirect uri you are looking for does not exist")
            return result[0]

    async def validate_client_redirect_uri(self, client_id: str, redirect_uri: str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            redirect_uri = await session.execute(
                select(
                    [
                        exists().where(
                            ClientRedirectUri.client_id == client_id,
                            ClientRedirectUri.redirect_uri == redirect_uri,
                        )
                    ]
                )
            )
            result = redirect_uri.first()
            if not result[0]:
                raise ClientRedirectUriError("Redirect uri you are looking for does not exist")
            return result[0]

    async def get_client_scopes(self, client_id:str) -> list:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            scopes = await session.execute(
                select(ClientScope).where(ClientScope.client_id == client_id)
            )

            result = []
            for scope in scopes:
                result.append(scope[0].scope)

            return result

    async def get_client_redirect_uris(self, client_id:str) -> list:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            uris = await session.execute(
                select(ClientRedirectUri).where(ClientRedirectUri.client_id == client_id)
            )

            result = []
            for uri in uris:
                result.append(uri[0].redirect_uri)

            return result

    async def get_client_claims(self, client_id:str) -> list:
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

    def __repr__(self):
        return "Client Repository"
