import pytest
from sqlalchemy import select

from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository, PersistentGrant
from src.data_access.postgresql.errors.persistent_grant import PersistentGrantNotFoundError


@pytest.mark.asyncio
class TestPersistentGrantRepository:

    async def test_create_new_grant(self, engine):
        persistent_grant_repo = PersistentGrantRepository(engine)

        await persistent_grant_repo.create(
            client_id=2,
            grant_data='iyuiyy',
            user_id=2,
            persistent_grant_type_id=1
        )

        grant = await persistent_grant_repo.get(persistent_grant_type_id=1, grant_data='iyuiyy')

        await persistent_grant_repo.delete(
            grant_data=grant.grant_data,
            persistent_grant_type_id=grant.persistent_grant_type_id
        )

        assert grant.user_id == 2
        assert grant.grant_data == 'iyuiyy'

    async def test_create_new_grant_not_full_data(self, engine):
        persistent_grant_repo = PersistentGrantRepository(engine)
        with pytest.raises(TypeError):
            await persistent_grant_repo.create(
                data="not_secret_code", user_id=77777
            )

    async def test_delete_persistent_grant_by_client_and_user_id(self, engine, connection):
        persistent_grant_repo = PersistentGrantRepository(engine)
        await persistent_grant_repo.create(
            client_id='santa',
            data='santa_brings_presents',
            user_id=3,
            grant_type='code'
        )
        await persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
            client_id='santa',
            user_id=3
        )
        grant = await persistent_grant_repo.exists(grant_type="code", data="santa_brings_presents")

        assert grant is False

    async def test_delete_persistent_grant_not_exist(self, engine):
        self.persistent_grant_repo = PersistentGrantRepository(engine)
        with pytest.raises(PersistentGrantNotFoundError):
            await self.persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
                client_id='not_exist',
                user_id=33333
            )

    async def test_check_if_grant_exists(self, engine):
        self.persistent_grant_repo = PersistentGrantRepository(engine)
        grant = await self.persistent_grant_repo.exists(grant_type='code', data='secret_code')

        assert grant is True

    async def test_check_if_grant_not_exists(self, engine):
        self.persistent_grant_repo = PersistentGrantRepository(engine)
        result = await self.persistent_grant_repo.exists(grant_type='not_exist', data='33333')
        assert result is False

    async def test_check_grant_by_client_and_user_ids(self, engine):
        self.persistent_grant_repo = PersistentGrantRepository(engine)
        grant = await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
            client_id='test_client',
            user_id=1
        )
        assert grant is True

    async def test_check_grant_by_client_and_user_ids_wrong_client(self, engine):
        self.persistent_grant_repo = PersistentGrantRepository(engine)
        with pytest.raises(PersistentGrantNotFoundError):
            await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id='not_exists',
                user_id=1
            )

    async def test_check_grant_by_client_and_user_ids_wrong_user(self, engine):
        self.persistent_grant_repo = PersistentGrantRepository(engine)
        with pytest.raises(PersistentGrantNotFoundError):
            await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id='test_client',
                user_id=88888
            )

    async def test_check_grant_by_client_and_user_ids_wrong_client_and_user(self, engine):
        self.persistent_grant_repo = PersistentGrantRepository(engine)
        with pytest.raises(PersistentGrantNotFoundError):
            await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id='not_exists',
                user_id=88888
            )

    async def test_deleting_grants(self, engine):
        persistent_grant_repo = PersistentGrantRepository(engine)
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

    async def test_deleting_non_existing_grant(self, engine):
        persistent_grant_repo = PersistentGrantRepository(engine)
        response = await persistent_grant_repo.delete(data='foo', grant_type='bar')

        assert response == 404

    async def test_creating_grant_without_providing_type(self, engine):
        persistent_grant_repo = PersistentGrantRepository(engine)
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

    async def test_get_client_id_by_data(self, engine):
        persistent_grant_repo = PersistentGrantRepository(engine)

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

    async def test_get_client_id_by_wrong_data(self, engine):
        persistent_grant_repo = PersistentGrantRepository(engine)

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
