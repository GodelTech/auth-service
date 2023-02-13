import pytest
from sqlalchemy import insert, delete

from src.data_access.postgresql.errors.user import (
    ClaimsNotFoundError,
    UserNotFoundError,
)
from src.data_access.postgresql.repositories.user import (
    User,
    UserRepository,
)
from tests.test_unit.fixtures import DEFAULT_USER


@pytest.mark.asyncio
class TestUserRepository:
    async def test_get_hash_password_user_not_exists(self, engine):
        self.user_repo = UserRepository(engine)
        with pytest.raises(UserNotFoundError):
            await self.user_repo.get_hash_password(user_name="not_exists_user")

    async def test_get_hash_password(self, engine, connection):
        expected_hash_password = (
            "$2b$12$RAC7jWdNn8Fudxc4OhudkOPK0eeBBWjGd5Iyfzma5F8uv9xD.jx/6"
        )
        self.user_repo = UserRepository(engine)

        # The sequence id number is out of sync and raises duplicate key error
        # We manually bring it back in sync
        await connection.execute(
            "SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users)+1);"
        )

        await connection.execute(insert(User).values(**DEFAULT_USER))
        await connection.commit()
        user_hash_password, user_id = await self.user_repo.get_hash_password(
            user_name="DefaultTestClient"
        )
        assert user_hash_password == expected_hash_password
        await connection.execute(
            delete(User).where(User.username == "DefaultTestClient")
        )
        await connection.commit()

    async def test_get_claims(self, engine):
        expected_given_name = "Ibragim"
        expected_nickname = "Nagibator2000"

        self.user_repo = UserRepository(engine)
        result = await self.user_repo.get_claims(id=1)

        assert result["given_name"] == expected_given_name
        assert result["nickname"] == expected_nickname

    async def test_get_claims_user_not_exists(self, engine):
        self.user_repo = UserRepository(engine)
        with pytest.raises(ClaimsNotFoundError):
            await self.user_repo.get_claims(id=55555)
