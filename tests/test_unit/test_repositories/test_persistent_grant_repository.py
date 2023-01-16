import pytest
from sqlalchemy import select, delete

from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrant,
    PersistentGrantRepository,
)


@pytest.mark.asyncio
class TestPersistentGrantRepository:

    async def test_create_new_grant(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id="double_test", data="secret_code", user_id=2
        )

        grant = await persistent_grant_repo.session.execute(
            select(PersistentGrant).where(
                PersistentGrant.client_id == "double_test"
            )
        )

        grant = grant.fetchall()
        assert grant[-1][0].subject_id == 2
        assert grant[-1][0].data == "secret_code"

    async def test_create_new_grant_not_full_data(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(TypeError):
            await persistent_grant_repo.create(
                data="not_secret_code", user_id=77777
            )

    async def test_get_client_id_by_data(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id="aragorn", data="secret_code_for_tes", user_id=6
        )
        client_id = await persistent_grant_repo.get_client_id_by_data(data="secret_code_for_tes")

        assert client_id == "aragorn"

        await persistent_grant_repo.session.execute(
                delete(PersistentGrant).
                where(PersistentGrant.client_id == "aragorn")
            )
        await persistent_grant_repo.session.commit()

    async def test_get_client_id_by_wrong_data(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id="aragorn", data="secret_code_for_tes", user_id=6
        )
        with pytest.raises(Exception):
            await persistent_grant_repo.get_client_id_by_data(data="data_not_exists")

        await persistent_grant_repo.session.execute(
                delete(PersistentGrant).
                where(PersistentGrant.client_id == "aragorn")
            )
        await persistent_grant_repo.session.commit()
