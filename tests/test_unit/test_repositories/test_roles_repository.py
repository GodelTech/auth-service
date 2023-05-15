import pytest
from sqlalchemy import delete
from sqlalchemy.future import select

from src.data_access.postgresql.repositories.roles import RoleRepository
from src.data_access.postgresql.errors.user import DuplicationError
from src.data_access.postgresql.tables.users import Role
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
class TestRoleRepository:

    async def test_exists(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        result = await role_repo.exists(role_id=2)

        assert result is True

    async def test_not_exists(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        result = await role_repo.exists(role_id=555555)

        assert result is False

    async def test_get_role_by_id(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        expected_role = "Journalist, broadcasting"
        role = await role_repo.get_role_by_id(2)

        assert role.name == expected_role

    async def test_get_role_by_id_not_exist(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        with pytest.raises(ValueError):
            await role_repo.get_role_by_id(77777)

    async def test_update_role(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        new_role = "fifth_element"
        await role_repo.update(role_id=5, name=new_role)
        updated_role = await role_repo.get_role_by_id(5)

        assert updated_role.name == new_role

    async def test_update_not_exist_role(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        new_role = "not_exist"
        try:
            await role_repo.update(role_id=-1, name=new_role)
        except ValueError:
            pass
        else:
            raise AssertionError

    async def test_create(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        new_role = "new_role"
        try:
            await role_repo.create(name=new_role)
        except:
            raise AssertionError
        role_id = (await role_repo.get_role_by_name(new_role)).id
        await role_repo.delete(role_id= role_id)

    async def test_create_duplicate(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        new_role = "Journalist, broadcasting"
        with pytest.raises(DuplicationError):
            await role_repo.create(name=new_role)

    async def test_get_all_roles(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        roles = await role_repo.get_all_roles()
        roles.sort(key=lambda x: x.id)

        assert isinstance(roles, list)
        assert roles[0].name == "Programmer, applications"

    async def test_delete(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        await role_repo.create(name="last_role")
        roles_id = await connection.execute(
            select(Role.id)
        )
        roles_id = [x[0] for x in roles_id.all()]
        roles_id.sort()
        await role_repo.delete(role_id=roles_id[-1])

        assert True

    async def test_delete_not_exist(self, connection: AsyncSession)-> None:
        role_repo = RoleRepository(connection)
        with pytest.raises(ValueError):
            await role_repo.delete(77777)
