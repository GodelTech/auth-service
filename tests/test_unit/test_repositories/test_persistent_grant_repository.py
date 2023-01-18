import pytest
from sqlalchemy import select, delete

from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository
)


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
        ) == True

        await persistent_grant_repo.delete(
            data='elekltklkte',
            grant_type='code'
        )

        assert await persistent_grant_repo.exists(
            grant_type='code',
            data='elekltklkte'
        ) == False


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
        ) == True
        
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
