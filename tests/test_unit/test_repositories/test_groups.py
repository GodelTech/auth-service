import pytest

from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories.groups import GroupRepository
from src.data_access.postgresql.tables.group import Group


@pytest.mark.usefixtures("engine", "pre_test_setup")
@pytest.mark.asyncio
class TestGroupRepository:
    async def test_create_delete_exist_not_exist(
        self, connection: AsyncSession
    ) -> None:
        group_repo = GroupRepository(connection)
        group_ids = await connection.execute(select(Group.id))
        group_ids = [x[0] for x in group_ids.all()]
        group_ids.sort()
        if len(group_ids) <= 1:
            group_id = 1
        else:
            group_id = group_ids[-1] + 1

        await group_repo.create(
            id=group_id, name="strange_name", parent_group=None
        )
        await connection.flush()
        created = await group_repo.exists(group_id=group_id)
        assert created is True

        await group_repo.delete(group_id=group_id)
        await connection.flush()
        deleted = await group_repo.exists(group_id=group_id)
        assert deleted is False

    async def test_create_existing(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        group_ids = await connection.execute(select(Group.id))
        group_ids = [x[0] for x in group_ids.all()]
        group_ids.sort()
        if len(group_ids) <= 1:
            group_id = 1
        else:
            group_id = group_ids[-1] + 1

        await group_repo.create(
            id=group_id, name="strange_name", parent_group=None
        )
        await connection.flush()
        created = await group_repo.exists(group_id=group_id)
        assert created is True
        with pytest.raises(exc.IntegrityError):
            await group_repo.create(
                id=group_id, name="strange_name", parent_group=None
            )

        # await group_repo.delete(group_id=group_id)
        # deleted = await group_repo.exists(group_id=group_id)
        # assert deleted is False

    async def test_delete_not_existing(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        with pytest.raises(ValueError):
            await group_repo.delete(group_id=55555)

    async def test_delete_all(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)

        await group_repo.delete()
        groups = await connection.execute(select(Group))
        groups = groups.all()
        assert groups == []

    async def test_get_by_id(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        group_ids = await connection.execute(select(Group.id))
        group_ids = [x[0] for x in group_ids.all()]
        group_ids.sort()
        if len(group_ids) <= 1:
            group_id = 1
        else:
            group_id = group_ids[-1] + 1
        await group_repo.create(
            id=group_id, name="strange_name", parent_group=None
        )

        group = await group_repo.get_by_id(group_id=group_id)
        assert group.name == "strange_name"
        await group_repo.delete(group_id=group_id)

    async def test_get_by_id_not_exist(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        with pytest.raises(ValueError):
            await group_repo.get_by_id(group_id=55555)

    async def test_get_by_name(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        group_ids = await connection.execute(select(Group.id))
        group_ids = [x[0] for x in group_ids.all()]
        group_ids.sort()
        if len(group_ids) <= 1:
            group_id = 1
        else:
            group_id = group_ids[-1] + 1
        await group_repo.create(
            id=group_id, name="strange_name", parent_group=None
        )

        group = await group_repo.get_group_by_name(name="strange_name")
        assert group.name == "strange_name"
        await group_repo.delete(group_id=group_id)

    async def test_get_by_name_not_exist(
        self, connection: AsyncSession
    ) -> None:
        group_repo = GroupRepository(connection)
        with pytest.raises(ValueError):
            await group_repo.get_group_by_name(name="pom_pon")

    async def test_get_all_groups(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        group_ids = await connection.execute(select(Group.id))
        group_ids = [x[0] for x in group_ids.all()]
        group_ids.sort()
        if len(group_ids) <= 1:
            group_id = 1
        else:
            group_id = group_ids[-1] + 1
        await group_repo.create(
            id=group_id, name="first_new_name", parent_group=None
        )
        await group_repo.create(
            id=(group_id + 1), name="second_new_name", parent_group=None
        )

        groups = await group_repo.get_all_groups()
        groups.sort(key=lambda x: x.id)

        assert groups[-1].name == "second_new_name"
        assert groups[-2].name == "first_new_name"

        await group_repo.delete(group_id=group_id)
        await group_repo.delete(group_id=(group_id + 1))

    async def test_get_all_subgroups(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        group_ids = await connection.execute(select(Group.id))
        group_ids = [x[0] for x in group_ids.all()]
        group_ids.sort()
        if len(group_ids) <= 1:
            group_id = 1
        else:
            group_id = group_ids[-1] + 1
        await group_repo.create(
            id=group_id, name="grand_parent", parent_group=None
        )
        await group_repo.create(
            id=(group_id + 1), name="parent", parent_group=group_id
        )
        await group_repo.create(
            id=(group_id + 2), name="child", parent_group=(group_id + 1)
        )
        expected_data = {
            f"subgroups_of_grand_parent_id_{group_id}": [
                {
                    "id": (group_id + 1),
                    "name": "parent",
                    "parent_group": group_id,
                    "subgroups": [
                        {
                            "id": (group_id + 2),
                            "name": "child",
                            "parent_group": (group_id + 1),
                            "subgroups": None,
                        }
                    ],
                }
            ]
        }
        main_group = await group_repo.get_group_by_name(name="grand_parent")
        subgroups = await group_repo.get_all_subgroups(main_group=main_group)

        assert subgroups == expected_data
        await group_repo.delete(group_id=(group_id + 2))
        await group_repo.delete(group_id=(group_id + 1))
        await group_repo.delete(group_id=group_id)

    async def test_update(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        group_ids = await connection.execute(select(Group.id))
        group_ids = [x[0] for x in group_ids.all()]
        group_ids.sort()
        if len(group_ids) <= 1:
            group_id = 1
        else:
            group_id = group_ids[-1] + 1
        await group_repo.create(
            id=group_id, name="first_new_name", parent_group=None
        )
        await group_repo.update(group_id=group_id, name="updated_name")
        updated_group = await group_repo.get_by_id(group_id=group_id)

        assert updated_group.name == "updated_name"
        await group_repo.delete(group_id=group_id)

    async def test_update_not_exist(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        with pytest.raises(ValueError):
            await group_repo.update(group_id=555555, name="updated_name")

    async def test_update_duplication_error(
        self, connection: AsyncSession
    ) -> None:
        group_repo = GroupRepository(connection)
        group_ids = await connection.execute(select(Group.id))
        group_ids = [x[0] for x in group_ids.all()]
        group_ids.sort()
        if len(group_ids) <= 1:
            group_id = 1
        else:
            group_id = group_ids[-1] + 1
        await group_repo.create(
            id=group_id, name="first_new_name", parent_group=None
        )
        await group_repo.create(
            id=(group_id + 1), name="parent", parent_group=None
        )
        await connection.flush()

        with pytest.raises(exc.IntegrityError):
            await group_repo.update(group_id=group_id, name="parent")

        # await group_repo.delete(group_id=group_id)
        # await group_repo.delete(group_id=(group_id + 1))
