from sqlalchemy import select

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.client import Client


class ClientRepository(BaseRepository):

    async def get_client_by_client_id(self, client_id: str):
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', client_id)
        session = self.session
        print('0000000000000000000000000000000000000000', session)
        client = await session.execute(select(Client).filter(Client.client_id == client_id))
        client = client.scalars().first()
        if client:
            return client
        else:
            return False

    def __repr__(self):
        return "Client Repository"
