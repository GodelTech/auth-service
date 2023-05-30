import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories import WellKnownRepository
from src.data_access.postgresql.tables.group import Group


@pytest.mark.asyncio
class TestWellKnownRepository:

    async def test_create_delete_exist_not_exist(self, connection: AsyncSession) -> None:
        wlk_repo = WellKnownRepository(connection)
        list_of_claims = await wlk_repo.get_user_claim_types()
        assert list_of_claims
