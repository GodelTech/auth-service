import pytest
from sqlalchemy import delete
from sqlalchemy.future import select

from src.data_access.postgresql.repositories.roles import RoleRepository
from src.data_access.postgresql.errors.user import DuplicationError
from src.data_access.postgresql.tables.users import Role


@pytest.mark.asyncio
class TestRoleRepository:

    async def test_exists(self, engine):
        role_repo = RoleRepository(engine)
        result = await role_repo.exists(role_id=2)

        assert result is True

    async def test_not_exists(self, engine):
        role_repo = RoleRepository(engine)
        result = await role_repo.exists(role_id=555555)

        assert result is False

    async def test_get_role_by_id(self, engine):
        role_repo = RoleRepository(engine)
        expected_role = "Journalist, broadcasting"
        role = await role_repo.get_role_by_id(2)

        assert role.name == expected_role

    async def test_get_role_by_id_not_exist(self, engine):
        role_repo = RoleRepository(engine)
        with pytest.raises(ValueError):
            await role_repo.get_role_by_id(77777)

    async def test_update_role(self, engine):
        role_repo = RoleRepository(engine)
        new_role = "fifth_element"
        updated = await role_repo.update(role_id=5, name=new_role)
        updated_role = await role_repo.get_role_by_id(5)

        assert updated is True
        assert updated_role.name == new_role

    async def test_update_not_exist_role(self, engine):
        role_repo = RoleRepository(engine)
        new_role = "not_exist"
        updated = await role_repo.update(role_id=55555, name=new_role)

        assert updated is False

    async def test_create(self, engine, connection):
        role_repo = RoleRepository(engine)
        new_role = "new_role"
        created = await role_repo.create(name=new_role)
        assert created is True

        await connection.execute(
            delete(Role).where(Role.name == new_role)
        )
        await connection.commit()

    async def test_create_duplicate(self, engine):
        role_repo = RoleRepository(engine)
        new_role = "Journalist, broadcasting"
        with pytest.raises(DuplicationError):
            await role_repo.create(name=new_role)

    async def test_get_all_roles(self, engine):
        role_repo = RoleRepository(engine)
        roles = await role_repo.get_all_roles()
        roles.sort(key=lambda x: x.id)

        assert isinstance(roles, list)
        assert roles[0].name == "Programmer, applications"

    async def test_delete(self, engine, connection):
        role_repo = RoleRepository(engine)
        await role_repo.create(name="last_role")
        roles_id = await connection.execute(
            select(Role.id)
        )
        roles_id = [x[0] for x in roles_id.all()]
        roles_id.sort()
        deleted = await role_repo.delete(role_id=roles_id[-1])

        assert deleted is True

    async def test_delete_not_exist(self, engine):
        role_repo = RoleRepository(engine)
        with pytest.raises(ValueError):
            await role_repo.delete(77777)
