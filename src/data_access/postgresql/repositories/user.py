from sqlalchemy import select

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.users import User


class UserRepository(BaseRepository):

    async def get_hash_password(self, user_name: str) -> str | bool:

        user = await self.session.execute(select(User).where(
            User.username == user_name
        ))
        try:
            user = user.first()[0]
            return user.password_hash
        except:
            return False
