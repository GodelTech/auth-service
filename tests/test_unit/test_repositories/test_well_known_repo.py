import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories import WellKnownRepository
from src.data_access.postgresql.tables.group import Group
from src.data_access.postgresql.errors.user import DuplicationError


@pytest.mark.asyncio
class TestWellKnownRepository:

    async def test_create_delete_exist_not_exist(self, engine: AsyncEngine, connection: AsyncSession) -> None:
        wlk_repo = WellKnownRepository(engine)
        list_of_claims = await wlk_repo.get_user_claim_types()
        assert list_of_claims
