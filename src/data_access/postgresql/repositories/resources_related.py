from typing import Union
from sqlalchemy import delete, exists, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import resources_related as res
from typing import Any, Dict, Union, Optional

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
        try:
            result = await self.session.execute(
                select(res.ApiResource).where(
                    res.ApiResource.id == api_res_id,
                )
            )
            return result.first()[0]
        except Exception as e:
            raise ValueError(e)


    async def get_by_name(self, name: str) -> res.ApiResource:
        try:
            group = await self.session.execute(
                select(res.ApiResource).where(res.ApiResource.name == name)
            )
            group = group.first()
            
            return group[0]
        except:
            raise ValueError


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
            raise ValueError(f"Api Resource id {api_res_id} does not exist")


    def __repr__(self) -> str:  # pragma: no cover
        return "Resorces Related repository"
