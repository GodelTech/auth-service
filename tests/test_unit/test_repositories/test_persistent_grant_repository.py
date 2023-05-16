import pytest
from sqlalchemy import select

from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
    PersistentGrant,
)
from src.data_access.postgresql.errors.persistent_grant import (
    PersistentGrantNotFoundError,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from typing import no_type_check


@pytest.mark.asyncio
class TestPersistentGrantRepository:
    async def test_create_new_grant(self, connection: AsyncSession) -> None:
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id="test_client",
            grant_data="iyuiyy",
            user_id=2,
            grant_type="authorization_code",
        )

        grant = await persistent_grant_repo.get(
            grant_type="authorization_code", grant_data="iyuiyy"
        )

        await persistent_grant_repo.delete(
            grant_data=grant.grant_data,
            grant_type=grant.persistent_grant_type.type_of_grant,
        )

        assert grant.user_id == 2
        assert grant.grant_data == "iyuiyy"

    @no_type_check
    async def test_create_new_grant_not_full_data(
        self, connection: AsyncSession
    ) -> None:
        persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(TypeError):
            await persistent_grant_repo.create(
                grant_data="not_secret_code", user_id=77777
            )

    async def test_delete_persistent_grant_by_client_and_user_id(
        self, connection: AsyncSession
    ) -> None:
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id="test_client",
            grant_data="santa_brings_presents",
            user_id=3,
            grant_type="authorization_code",
        )
        await persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
            client_id="test_client", user_id=3
        )
        grant = await persistent_grant_repo.exists(
            grant_type="authorization_code", grant_data="santa_brings_presents"
        )

        assert grant is False

    async def test_delete_persistent_grant_not_exist(
        self, connection: AsyncSession
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(PersistentGrantNotFoundError):
            await self.persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
                client_id="-1None", user_id=-1
            )

    # async def test_check_if_grant_exists(self, engine):
    #     self.persistent_grant_repo = PersistentGrantRepository(connection)

    #     grant = await self.persistent_grant_repo.exists(grant_type='code', grant_data='secret_code')

    #     assert grant is True

    async def test_check_if_grant_not_exists(self, connection: AsyncSession) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        result = await self.persistent_grant_repo.exists(
            grant_type="not_exist", grant_data="33333"
        )
        assert result is False

    async def test_check_grant_by_client_and_user_ids(
        self, connection: AsyncSession
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        await self.persistent_grant_repo.create(
            client_id="test_client",
            grant_data="test_check_grant_by_client_and_user_ids",
            user_id=1,
            grant_type="authorization_code",
        )

        grant = (
            await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id="test_client", user_id=1
            )
        )
        assert grant is True
        await self.persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
            client_id="test_client", user_id=1
        )

    async def test_check_grant_by_client_and_user_ids_wrong_client(
        self, connection: AsyncSession
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(PersistentGrantNotFoundError):
            await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id="-1None", user_id=1
            )

    async def test_check_grant_by_client_and_user_ids_wrong_user(
        self, connection: AsyncSession
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(PersistentGrantNotFoundError):
            await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id="test_client", user_id=-1
            )

    async def test_check_grant_by_client_and_user_ids_wrong_client_and_user(
        self, connection: AsyncSession
    ) -> None:
        self.persistent_grant_repo = PersistentGrantRepository(connection)
        with pytest.raises(PersistentGrantNotFoundError):
            await self.persistent_grant_repo.check_grant_by_client_and_user_ids(
                client_id="-1None", user_id=-1
            )

    async def test_deleting_grants(self, connection: AsyncSession) -> None:
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id="test_client",
            grant_data="elekltklkte",
            user_id=2,
            grant_type="authorization_code",
        )

        assert (
            await persistent_grant_repo.exists(
                grant_type="authorization_code", grant_data="elekltklkte"
            )
            is True
        )

        await persistent_grant_repo.delete(
            grant_data="elekltklkte", grant_type="authorization_code"
        )

        assert (
            await persistent_grant_repo.exists(
                grant_type="authorization_code", grant_data="elekltklkte"
            )
            is False
        )

    async def test_deleting_non_existing_grant(
        self, connection: AsyncSession
    ) -> None:
        persistent_grant_repo = PersistentGrantRepository(connection)
        response = await persistent_grant_repo.delete(
            grant_data="foo", grant_type="bar"
        )

        assert response == 404

    async def test_creating_grant_without_providing_type(
        self, connection: AsyncSession
    ) -> None:
        persistent_grant_repo = PersistentGrantRepository(connection)
        await persistent_grant_repo.create(
            client_id="test_client", grant_data="secret_code", user_id=2
        )

        assert (
            await persistent_grant_repo.exists(
                grant_type="authorization_code", grant_data="secret_code"
            )
            is True
        )

        grant = await persistent_grant_repo.get(
            grant_type="authorization_code", grant_data="secret_code"
        )
        await persistent_grant_repo.delete(
            grant_data=grant.grant_data,
            grant_type=grant.persistent_grant_type.type_of_grant,
        )

    async def test_get_client_id_by_data(self, connection: AsyncSession) -> None:
        persistent_grant_repo = PersistentGrantRepository(connection)

        await persistent_grant_repo.create(
            client_id="test_client",
            grant_data="test_get_client_id_by_data",
            user_id=6,
        )
        client_id = await persistent_grant_repo.get_client_id_by_data(
            grant_data="test_get_client_id_by_data"
        )

        assert client_id == "test_client"

        grant = await persistent_grant_repo.get(
            grant_type="authorization_code",
            grant_data="test_get_client_id_by_data",
        )
        await persistent_grant_repo.delete(
            grant_data=grant.grant_data,
            grant_type=grant.persistent_grant_type.type_of_grant,
        )

    async def test_get_client_id_by_wrong_data(
        self, connection: AsyncSession
    ) -> None:
        persistent_grant_repo = PersistentGrantRepository(connection)

        with pytest.raises(Exception):
            await persistent_grant_repo.get_client_id_by_data(
                grant_data="test_get_client_id_by_wrong_data"
            )
