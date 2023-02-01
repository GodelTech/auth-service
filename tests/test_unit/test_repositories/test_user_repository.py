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
        await connection.execute(
            insert(User).values(**DEFAULT_USER)
        )
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

    async def test_all(self, engine):
        self.user_repo = UserRepository(engine)
        
        a = await self.user_repo.add_group(user_id=1, group_id=1)
        b = await self.user_repo.add_group(user_id=1, group_id=2)
        c = await self.user_repo.remove_user_groups(user_id=1, group_ids=[2])
        c2= await self.user_repo.get_groups(1)
        d = await self.user_repo.add_group(user_id=1, group_id=3)
        e = await self.user_repo.get_roles(user_id=1)        
        f = await self.user_repo.get_groups(user_id=1)
        assert f