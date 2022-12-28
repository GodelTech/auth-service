import pytest
from sqlalchemy import select, insert

from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.user import User, UserClaim
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository, PersistentGrant
from src.data_access.postgresql.repositories.user import UserRepository
from tests.test_unit.fixtures import DEFAULT_USER, DEFAULT_USER_CLAIMS
from src.data_access.postgresql.errors.client import ClientNotFoundError
from src.data_access.postgresql.errors.user import UserNotFoundError


@pytest.mark.asyncio
class TestPersistentGrantRepository:

    async def test_create_new_grant(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        await self.persistent_grant_repo.create_new_grant(
            client_id='double_test',
            secret_code='secret_code',
            user_id=2
        )

        grant = await self.persistent_grant_repo.session. \
            execute(select(PersistentGrant).where(PersistentGrant.client_id == 'double_test'))

        grant = grant.fetchall()
        assert grant[-1][0].subject_id == 2
        assert grant[-1][0].data == 'secret_code'

    async def test_create_new_grant_not_full_data(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(TypeError):
            await self.persistent_grant_repo.create_new_grant(
                secret_code='not_secret_code',
                user_id=777
            )