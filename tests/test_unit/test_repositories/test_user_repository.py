import pytest
from sqlalchemy import insert

from src.data_access.postgresql.errors.user import (
    ClaimsNotFoundError,
    UserNotFoundError,
)
from src.data_access.postgresql.repositories.user import (
    User,
    UserClaim,
    UserRepository,
)
from tests.test_unit.fixtures import DEFAULT_USER, DEFAULT_USER_CLAIMS


@pytest.mark.asyncio
class TestUserRepository:
    async def test_get_hash_password_user_not_exists(self, connection):
        self.user_repo = UserRepository(connection)
        with pytest.raises(UserNotFoundError):
            await self.user_repo.get_hash_password(user_name="not_exists_user")

    async def test_get_hash_password(self, connection):
        expected_hash_password = (
            "$2b$12$RAC7jWdNn8Fudxc4OhudkOPK0eeBBWjGd5Iyfzma5F8uv9xD.jx/6"
        )
        self.user_repo = UserRepository(connection)
        await self.user_repo.session.execute(
            insert(User).values(**DEFAULT_USER)
        )

        user_hash_password, user_id = await self.user_repo.get_hash_password(
            user_name="DefaultTestClient"
        )

        assert user_hash_password == expected_hash_password

    async def test_get_claims(self, connection):
        expected_given_name = "Ibragim"
        expected_nickname = "Nagibator2000"

        self.user_repo = UserRepository(connection)
        result = await self.user_repo.get_claims(id=1)

        assert result["given_name"] == expected_given_name
        assert result["nickname"] == expected_nickname

    async def test_get_claims_user_not_exists(self, connection):
        self.user_repo = UserRepository(connection)
        with pytest.raises(ClaimsNotFoundError):
            await self.user_repo.get_claims(id=55555)
