import pytest
from src.data_access.postgresql.repositories import (
    PersistentGrantRepository,
    BlacklistedTokenRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.celery_logic.token_tasks import clear_database


@pytest.mark.usefixtures("engine", "pre_test_setup")
@pytest.mark.asyncio
class TestTokenTasks:
    async def test_clear_database(self, connection: AsyncSession) -> None:
        persistent_grant_repo = PersistentGrantRepository(connection)
        blacklisted_repo = BlacklistedTokenRepository(connection)
        await persistent_grant_repo.create(
            client_id="test_client",
            grant_data="to_delete",
            user_id=2,
            grant_type="authorization_code",
            expiration_time=0
        )
        await persistent_grant_repo.create(
            client_id="test_client",
            grant_data="to_delete2",
            user_id=2,
            grant_type="authorization_code",
            expiration_time=0
        )
        await blacklisted_repo.create(
            token="to_delete2",
            expiration=0
        )
        await connection.commit()
        
        responce = clear_database()

        assert responce == "Total deleted: 3"
        assert not await persistent_grant_repo.exists(grant_data='to_delete', grant_type='authorization_code')
        assert not await blacklisted_repo.exists(token='to_delete2')

    async def test_no_expired(self, connection: AsyncSession) -> None:
        responce = clear_database()
        assert responce == "Total deleted: 0"
        
