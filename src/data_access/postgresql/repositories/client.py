from sqlalchemy import select, and_

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.client import Client
# from src.data_access.postgresql.tables.user import User


class ClientRepository(BaseRepository):

    async def get_client_by_client_id(self, client_id: str):
        client = await self.session.execute(select(Client).where(Client.client_id == client_id))
        client = client.first()[0]
        if client:
            return client
        else:
            return False

    # async def generate_code_by_user_name_and_password(self, user_name: str, password: str):
    #     user = await self.session.execute(select(User).where(and_(
    #         User.user_name == user_name,
    #         User.password == password
    #     )))
    #     user = user.first()[0]
    #     if user:
    #         pass # functionality to generate code and redirect

    def __repr__(self):
        return "Client Repository"
