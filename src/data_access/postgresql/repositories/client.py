import secrets

from sqlalchemy import select

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.client import Client


class ClientRepository(BaseRepository):

    async def get_client_by_client_id(self, client_id: str):
        client = await self.session.execute(select(Client).where(Client.client_id == client_id))
        try:
            client = client.first()[0]
            return client
        except:
            return False

    def __repr__(self):
        return "Client Repository"
