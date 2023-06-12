from typing import Union
from sqlalchemy import delete, exists, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import resources_related as res
from typing import Any, Dict, Union, Optional
from ..errors import resource as err


def params_to_dict(**kwargs: Any) -> Dict[str, Any]:
    result = {}
    for key in kwargs:
        if kwargs[key] is not None:
            result[key] = kwargs[key]
    return result


class ResourcesRepository(BaseRepository):
    async def create(self,) -> None:
        pass


    async def delete(self,) -> None:
        pass


    async def exists(self, api_res_id: int) -> bool:
        result = await self.session.execute(
            select(exists().where(res.ApiResource.id == api_res_id))
        )
        result = result.first()
        return result[0]


    async def get_by_id(self, api_res_id: int) -> res.ApiResource:
        result = await self.session.execute(
            select(res.ApiResource).where(
                res.ApiResource.id == api_res_id,
            )
        )

        resource = result.first()
        if resource is None:
            raise err.ResourceNotFoundError(str(api_res_id))
        if not resource[0].enabled:
            raise err.ResourceDisabledError(f"{resource[0].name} enabled: {resource[0].enabled}")
        return resource[0]

    async def get_by_name(self, name: str) -> res.ApiResource:
        result = await self.session.execute(
            select(res.ApiResource).where(res.ApiResource.name == name)
        )
        result = result.first()

        if result is None:
            raise err.ResourceNotFoundError(name)
        
        resource = result[0]
        if not resource.enabled:
            raise err.ResourceDisabledError(f"{resource.name} enabled: {resource.enabled}")
        
        return resource


    async def get_all(self) -> list[res.ApiResource]:
        resources = await self.session.execute(select(res.ApiResource))
        result = [resource[0] for resource in resources]
        return result


    async def update_resource(self, api_res_id: int,**kwargs) -> None:
        if await self.exists(api_res_id==api_res_id):
            updates = (
                update(res.ApiResource)
                .values(**kwargs)
                .where(res.ApiResource.id == api_res_id)
            )
            await self.session.execute(updates)
        else:
            raise err.ResourceNotFoundError(f"Api Resource id {api_res_id} does not exist")

    async def get_scope_claims(self, resource_name: str, scope_name: str) -> list[str]:
        join_condition = res.ApiResource.name == resource_name and res.ApiResource.id == res.ApiScope.api_resources_id and res.ApiScope.name == scope_name
        result = await self.session.execute(
            select(res.ApiScopeClaim.scope_claim_type).join(res.ApiResource).join(res.ApiScope).where(join_condition)
        )
        return [scope_claim_type[0].scope_claim_type for scope_claim_type in result]
   
    def __repr__(self) -> str:  # pragma: no cover
        return "Resorces Related repository"
