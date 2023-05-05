from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

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
            raise ClientNotFoundError(
                "Client you are looking for does not exist"
            )
        return result[0]

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
        # session_factory = sessionmaker(
        #     self.engine, expire_on_commit=False, class_=AsyncSession
        # )
        # async with session_factory() as sess:
        #     session = sess
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

    async def get_client_scopes(self, client_id: int) -> str:
        scopes = await self.session.execute(
            select(ClientScope).where(ClientScope.client_id == client_id)
        )
        return scopes.first()[-1].scope

    async def get_client_redirect_uris(self, client_id: int) -> list[str]:
        uris = await self.session.execute(
            select(ClientRedirectUri)
            .join(Client, ClientSecret.client_id == Client.id)
            .where(Client.client_id == client_id)
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

    async def list_all_scopes_by_client(self, client_id: str) -> str:
        scopes = await self.session.scalars(
            select(ClientScope.scope)
            .join(Client, ClientScope.client_id == Client.id)
            .where(Client.client_id == client_id)
        )
        return scopes.all()

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

    def __repr__(self) -> str:
        return "Client Repository"
