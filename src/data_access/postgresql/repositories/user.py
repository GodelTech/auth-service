from sqlalchemy import select

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.users import User, UserClaim
from src.data_access.postgresql.errors.user import UserNotFoundError


class UserRepository(BaseRepository):

    async def get_hash_password(self, user_name: str) -> tuple:

        user = await self.session.execute(select(User).where(
            User.username == user_name
        ))
        user = user.first()

        if user is None:
            raise UserNotFoundError("User you are looking for does not exist")

        user = user[0]
        return user.password_hash, user.id

    async def get_claims(self, id: int) -> dict:

        claims_of_user = await self.session.execute(select(UserClaim).where(UserClaim.user_id == id))
        result = {}

        for claim in claims_of_user:
            result[dict(claim)["UserClaim"].claim_type.code] = dict(claim)["UserClaim"].claim_value

        return result

    def __repr__(self) -> str:
        return "User repository"
