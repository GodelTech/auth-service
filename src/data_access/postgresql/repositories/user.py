from sqlalchemy import select

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.users import User
from src.data_access.postgresql.errors.user import UserNotFoundError


class UserRepository(BaseRepository):

    async def get_hash_password(self, user_name: str) -> str:

        user = await self.session.execute(select(User).where(
            User.username == user_name
        ))
        user = user.first()

        if user is None:
            raise UserNotFoundError("User you are looking for does not exist")

        user = user[0]
        return user.password_hash

    def __repr__(self) -> str:
        return "User repository"

