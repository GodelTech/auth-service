from sqlalchemy import select

from src.data_access.postgresql.errors.client import ClientNotFoundError
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.client import Client


class ClientRepository(BaseRepository):

    async def get_client_by_client_id(self, client_id: str) -> bool:
        client = await self.session.execute(select(Client).where(Client.client_id == client_id))
        client = client.first()
        if client is None:
            raise ClientNotFoundError("Client you are looking for does not exist")
        return bool(client)

    def __repr__(self):
        return "Client Repository"
