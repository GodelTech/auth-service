import pytest

from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories.resources_related import ResourcesRepository
from src.data_access.postgresql.tables.resources_related import ApiResource



@pytest.mark.asyncio
class TestResourcesRepository:

    async def test_get(self, connection: AsyncSession) -> None:
        res_repo = ResourcesRepository(connection)
        resource_1 = await res_repo.get_by_id(api_res_id=1)
        resource_2  = await res_repo.get_by_name(resource_1.name)
        assert resource_1.name == resource_2.name and resource_1.id == resource_2.id , "'get_by_id' result is not equal to 'get_by_name'"

        all_resources = await res_repo.get_all()
        assert resource_1 in all_resources, "get_all() doesn't work"

        all_scope_claims = await res_repo.get_scope_claims(resource_name='oidc', scope_name='userinfo')
        assert all_scope_claims is list and all_scope_claims[0] is str, "get_scope_claims() doesn't work"

    