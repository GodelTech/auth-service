import pytest

from src.data_access.postgresql.tables.rsa_keys import RSA_keys
# from src.data_access.postgresql.errors.user import (
#     ClaimsNotFoundError,
#     UserNotFoundError,
# )
from src.data_access.postgresql.repositories.rsa_keys import RSAKeysRepository
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
class TestRSAKeysRepository:
    async def test_get_keys_from_repository(
            self, engine: AsyncEngine, connection: AsyncSession) -> None:
        rsa_keys_repo = RSAKeysRepository(connection)

        rsa_keys = RSA_keys()
        rsa_keys.private_key = b"test_private_key"
        rsa_keys.public_key = b"test_public_key"
        rsa_keys.n = 123
        rsa_keys.e = 123

        await rsa_keys_repo.put_keys_to_repository(rsa_keys)

        rsa_keys_from_db = await rsa_keys_repo.get_keys_from_repository()

        assert isinstance(rsa_keys_from_db, RSA_keys)
        assert hasattr(rsa_keys_from_db, "private_key")
        assert hasattr(rsa_keys_from_db, "public_key")
        assert hasattr(rsa_keys_from_db, "n")
        assert hasattr(rsa_keys_from_db, "e")

    async def test_get_keys_from_repository_not_exist(
            self, connection: AsyncSession) -> None:
        rsa_keys_repo = RSAKeysRepository(connection)

        rsa_keys = await rsa_keys_repo.get_keys_from_repository()
        assert rsa_keys is None

    async def test_put_keys_to_repository(self, connection: AsyncSession) -> None:
        rsa_keys_repo = RSAKeysRepository(connection)

        rsa_keys = RSA_keys()
        rsa_keys.private_key = b"test_private_key"
        rsa_keys.public_key = b"test_public_key"
        rsa_keys.n = 12345
        rsa_keys.e = 12345

        await rsa_keys_repo.put_keys_to_repository(rsa_keys)

        rsa_keys_from_db = await rsa_keys_repo.get_keys_from_repository()
        assert rsa_keys_from_db.private_key == b"test_private_key"
        assert rsa_keys_from_db.public_key == b"test_public_key"
        assert rsa_keys_from_db.n == 12345
        assert rsa_keys_from_db.e == 12345

    async def test_validate_keys_exist(self, connection: AsyncSession) -> None:
        rsa_keys_repo = RSAKeysRepository(connection)
        exist = await rsa_keys_repo.validate_keys_exists()

        assert exist is False

        rsa_keys = RSA_keys(
            private_key=b"some_private_key",
            public_key=b"some_public_key",
            n=12345,
            e=12345,
        )
        await rsa_keys_repo.put_keys_to_repository(rsa_keys)

        exist = await rsa_keys_repo.validate_keys_exists()
        assert exist is True

    async def test_validate_keys_not_exist(self, connection: AsyncSession) -> None:
        rsa_keys_repo = RSAKeysRepository(connection)

        exist = await rsa_keys_repo.validate_keys_exists()
        assert exist is False



