import pytest
from sqlalchemy import select, delete

from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository, PersistentGrant
from src.data_access.postgresql.errors.persistent_grant import PersistentGrantNotFoundError


@pytest.mark.asyncio
class TestPersistentGrantRepository:

    async def test_create_new_grant(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id='double_test',
            data='iyuiyy',
            user_id=2,
            grant_type='code'
        )

        grant = await persistent_grant_repo.get(grant_type='code', data='iyuiyy')

        await persistent_grant_repo.delete(
            data=grant.data,
            grant_type=grant.type
        )

        assert grant.subject_id == 2
        assert grant.data == 'iyuiyy'

    async def test_create_new_grant_not_full_data(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(TypeError):
            await persistent_grant_repo.create(
                data="not_secret_code", user_id=77777
            )

    async def test_delete_persistent_grant_by_client_and_user_id(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        await self.persistent_grant_repo.create(
            client_id='santa',
            data='santa_brings_presents',
            user_id=3,
            grant_type='code'
        )
        await self.persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
            client_id='santa',
            user_id=3
        )
        grant = await self.persistent_grant_repo.session. \
            execute(select(PersistentGrant).where(PersistentGrant.client_id == 'santa'))
        grant = grant.first()

        assert grant is None

    async def test_delete_persistent_grant_not_exist(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(PersistentGrantNotFoundError):
            await self.persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
                client_id='not_exist',
                user_id=33333
            )

    async def test_check_if_grant_exists(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        grant = await self.persistent_grant_repo.exists(grant_type='code', data='secret_code')

        assert grant is True

    async def test_check_if_grant_not_exists(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        result = await self.persistent_grant_repo.exists(grant_type='not_exist', data='33333')
        assert result is False

    async def test_check_grant_by_client_and_user_ids(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        grant = await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
            client_id='test_client',
            user_id=1
        )
        assert grant is True

    async def test_check_grant_by_client_and_user_ids_wrong_client(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(PersistentGrantNotFoundError):
            grant = await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id='not_exists',
                user_id=1
            )

    async def test_check_grant_by_client_and_user_ids_wrong_user(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(PersistentGrantNotFoundError):
            grant = await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id='test_client',
                user_id=88888
            )

    async def test_check_grant_by_client_and_user_ids_wrong_client_and_user(self, connection):
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(PersistentGrantNotFoundError):
            grant = await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id='not_exists',
                user_id=88888
            )

    async def test_deleting_grants(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id='double_test',
            data='elekltklkte',
            user_id=2,
            grant_type='code'
        )

        assert await persistent_grant_repo.exists(
            grant_type='code',
            data='elekltklkte'
        ) is True

        await persistent_grant_repo.delete(
            data='elekltklkte',
            grant_type='code'
        )

        assert await persistent_grant_repo.exists(
            grant_type='code',
            data='elekltklkte'
        ) is False

    async def test_deleting_non_existing_grant(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)
        response = await persistent_grant_repo.delete(data='foo', grant_type='bar')

        assert response == 404

    async def test_creating_grant_without_providing_type(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id='double_test',
            data='secret_code',
            user_id=2)

        assert await persistent_grant_repo.exists(
            grant_type='code',
            data='secret_code'
        ) is True

        grant = await persistent_grant_repo.get(grant_type='code', data='secret_code')
        await persistent_grant_repo.delete(
            data=grant.data,
            grant_type=grant.type
        )

    async def test_get_client_id_by_data(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)

        await persistent_grant_repo.create(
            client_id="aragorn", data="secret_code_for_tes", user_id=6
        )
        client_id = await persistent_grant_repo.get_client_id_by_data(data="secret_code_for_tes")

        assert client_id == "aragorn"

        grant = await persistent_grant_repo.get(grant_type='code', data='secret_code_for_tes')
        await persistent_grant_repo.delete(
            data=grant.data,
            grant_type=grant.type
        )

    async def test_get_client_id_by_wrong_data(self, connection):
        persistent_grant_repo = PersistentGrantRepository(connection)

        await persistent_grant_repo.create(
            client_id="aragorn", data="secret_code_for_tes", user_id=6
        )
        with pytest.raises(Exception):
            await persistent_grant_repo.get_client_id_by_data(data="data_not_exists")

        grant = await persistent_grant_repo.get(grant_type='code', data='secret_code_for_tes')
        await persistent_grant_repo.delete(
            data=grant.data,
            grant_type=grant.type
        )
