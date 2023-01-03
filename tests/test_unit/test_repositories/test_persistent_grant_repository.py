import pytest
from sqlalchemy import select

from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrant,
    PersistentGrantRepository,
)


@pytest.mark.asyncio
class TestPersistentGrantRepository:
    async def test_create_new_grant(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        await self.persistent_grant_repo.create(
            client_id="double_test", data="secret_code", user_id=2
        )

        grant = await self.persistent_grant_repo.session.execute(
            select(PersistentGrant).where(
                PersistentGrant.client_id == "double_test"
            )
        )

        grant = grant.fetchall()
        assert grant[-1][0].subject_id == 2
        assert grant[-1][0].data == "secret_code"

    async def test_create_new_grant_not_full_data(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(TypeError):
            await self.persistent_grant_repo.create(
                data="not_secret_code", user_id=77777
            )
