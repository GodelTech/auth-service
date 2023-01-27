import pytest
from pprint import pprint
from src.data_access.postgresql.repositories.groups import GroupRepository

GROUPS = [
    {
        "id" : 1,
        "name": "Jorno",
        "parent_group": None 
    },
    {
        "id" : 11,
        "name": 'gold',
        "parent_group": 1
    },
    {
        "id" : 12,
        "name": 'experience',
        "parent_group": 1
    },
    {
        "id" : 13,
        "name": 'requiem',
        "parent_group": 1
    },
    {
        "id" : 2,
        "name": "Polnareff",
        "parent_group": None
    },
    {
        "id" : 21,
        "name": 'silver',
        "parent_group": 2
    },
    {
        "id" : 201,
        "name": 'chariot',
        "parent_group": 21   
    },
    {
        "id" : 202,
        "name": 'requiem',
        "parent_group": 21
    },
    {
        "id" : 3,
        "name": 'Kakyoin',
        "parent_group": None
    },
    {
        "id" : 31,
        "name": 'hierophant',
        "parent_group": 3
    },
    {
        "id" : 32,
        "name": 'green',
        "parent_group": 3
    },
]

@pytest.mark.asyncio
class TestGroupRepository:

    async def test_setup(self, engine):
        group_repo = GroupRepository(engine)
        await group_repo.delete()        

        for group in GROUPS:
            await group_repo.create(name=group["name"], parent_group=group["parent_group"], id = group['id'])

        assert await group_repo.get_by_id(group_id=3)

    async def test_get_all_groups(self, engine):
        group_repo = GroupRepository(engine)
        groups = await group_repo.get_all_groups(
        )
        print(groups)
        assert bool(groups)

    async def test_get_subgroups(self, engine):
        group_repo = GroupRepository(engine)
        groups = await group_repo.get_all_groups()
        main_group = ...
        for group in groups:
            if group.name == "Polnareff":
                main_group = group
        
        groups = await group_repo.get_all_subgroups(
            main_group=main_group
        )

        assert groups