import pytest
from sqlalchemy import insert, delete, text, update

from data_access.postgresql.tables.rsa_keys import RSA_keys
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

        # Assuming that we have an RSA_keys instance
        rsa_keys1 = RSA_keys()
        rsa_keys1.private_key = "test_private_key1"
        rsa_keys1.public_key = "test_public_key1"
        rsa_keys1.n = "test_n1"
        rsa_keys1.e = "test_e1"

        rsa_keys2 = RSA_keys()
        rsa_keys2.private_key = "test_private_key2"
        rsa_keys2.public_key = "test_public_key2"
        rsa_keys2.n = "test_n2"
        rsa_keys2.e = "test_e2"

        await rsa_keys_repo.put_keys_to_repository(rsa_keys1)
        await rsa_keys_repo.put_keys_to_repository(rsa_keys2)

        rsa_keys = await rsa_keys_repo.get_keys_from_repository()

        assert isinstance(rsa_keys, RSA_keys)
        assert hasattr(rsa_keys, "private_key")
        assert hasattr(rsa_keys, "public_key")
        assert hasattr(rsa_keys, "n")
        assert hasattr(rsa_keys, "e")

    async def test_put_keys_to_repository(self, connection: AsyncSession) -> None:
        rsa_keys_repo = RSAKeysRepository(connection)

        rsa_keys = RSA_keys()
        rsa_keys.private_key = "test_private_key"
        rsa_keys.public_key = "test_public_key"
        rsa_keys.n = "test_n"
        rsa_keys.e = "test_e"

        await rsa_keys_repo.put_keys_to_repository(rsa_keys)

        rsa_keys_from_db = await rsa_keys_repo.get_keys_from_repository()
        assert rsa_keys_from_db.private_key == "test_private_key"
        assert rsa_keys_from_db.public_key == "test_public_key"
        assert rsa_keys_from_db.n == "test_n"
        assert rsa_keys_from_db.e == "test_e"

    async def test_validate_keys_exists(self, connection: AsyncSession) -> None:
        rsa_keys_repo = RSAKeysRepository(connection)

        assert not await rsa_keys_repo.validate_keys_exists()

        rsa_keys = RSA_keys()
        rsa_keys.private_key = "test_private_key"
        rsa_keys.public_key = "test_public_key"
        rsa_keys.n = "test_n"
        rsa_keys.e = "test_e"

        await rsa_keys_repo.put_keys_to_repository(rsa_keys)

        assert await rsa_keys_repo.validate_keys_exists()



