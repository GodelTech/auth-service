from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors.client import ClientNotFoundError, ClientPostLogoutRedirectUriError
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.client import Client, ClientPostLogoutRedirectUri, ClientSecret


class ClientRepository(BaseRepository):
    async def get_client_by_client_id(self, client_id: str) -> bool:
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
            return bool(client)

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
                select(ClientPostLogoutRedirectUri).
                where(ClientPostLogoutRedirectUri.client_id == client_id).
                where(ClientPostLogoutRedirectUri.post_logout_redirect_uri == logout_redirect_uri)
            )
            redirect_uri = logout_redirect_uri.first()
            if redirect_uri is None:
                raise ClientPostLogoutRedirectUriError("Post logout redirect uri you are looking for does not exist")
            return bool(redirect_uri)

    def __repr__(self):
        return "Client Repository"
