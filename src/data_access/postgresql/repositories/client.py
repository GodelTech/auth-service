import secrets

from fastapi import HTTPException, status
from sqlalchemy import select

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.client import Client


class ClientRepository(BaseRepository):

    async def get_client_by_client_id(self, client_id: str):
        client = await self.session.execute(select(Client).where(Client.client_id == client_id))
        client = client.first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return client[0]

    def __repr__(self):
        return "Client Repository"
