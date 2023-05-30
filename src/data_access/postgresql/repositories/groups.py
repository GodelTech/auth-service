from typing import Union

from sqlalchemy import delete, exists, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors.user import DuplicationError
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.group import *
from typing import Any, Dict, Union, Optional

def params_to_dict(**kwargs: Any) -> Dict[str, Any]:
    result = {}
    for key in kwargs:
        if kwargs[key] is not None:
            result[key] = kwargs[key]
    return result


class GroupRepository(BaseRepository):
    async def create(
        self, name: str, parent_group: Optional[int] = None, id: Optional[int] = None
    ) -> None:
        kwargs = params_to_dict(
            name=name, parent_group=parent_group, id=id
        )
        await self.session.execute(insert(Group).values(**kwargs))

    async def delete(self, group_id: Optional[int] = None) -> None:

        if group_id is None:
            await self.session.execute(text("DELETE FROM groups"))
        elif await self.exists(group_id=group_id):
            client_to_delete = await self.get_by_id(group_id=group_id)
            await self.session.delete(client_to_delete)
        else:
            raise ValueError

    async def exists(self, group_id: int) -> bool:

        result = await self.session.execute(
            select(exists().where(Group.id == group_id))
        )
        result = result.first()
        return result[0]

    async def get_by_id(self, group_id: int) -> Group:
        try:
            result = await self.session.execute(
                select(Group).where(
                    Group.id == group_id,
                )
            )
            return result.first()[0]
        except Exception as e:
            raise ValueError(e)

    async def get_group_by_name(self, name: str) -> Group:
        try:
            group = await self.session.execute(
                select(Group).where(Group.name == name)
            )
            group = group.first()
            
            return group[0]
        except:
            raise ValueError

    async def get_all_groups(self) -> list[Group]:
        groups = await self.session.execute(select(Group))
        result = [group[0] for group in groups]

        return result

    async def update(
        self, group_id: int, name: Optional[str] = None, parent_group: Optional[int] = None
    ) -> None:
        try:
            kwargs = params_to_dict(name=name, parent_group=parent_group)
            if await self.exists(group_id=group_id):
                updates = (
                    update(Group)
                    .values(**kwargs)
                    .where(Group.id == group_id)
                )
                await self.session.execute(updates)
            else:
                raise ValueError

        except ValueError:
            raise ValueError

    async def get_all_subgroups(self, main_group: Group) -> dict[str, Any]:
        all_groups = await self.get_all_groups()

        result = {
            f"subgroups_of_{main_group.name}_id_{main_group.id}": self.recursion(
                main_group=main_group.dictionary(), all_groups=all_groups
            )
        }
        return result

    # TODO move to services
    def recursion(
        self, main_group: dict[str, Any], all_groups: list[Any]
    ) -> Union[list[dict[str, Any]], None]:
        result = []
        groups_remove = []
        for group in all_groups:
            if main_group["id"] == group.parent_group:
                result.append(group.dictionary() | {"subgroups": ...})
                groups_remove.append(group)

        for group in groups_remove:
            all_groups.remove(group)

        if len(result) == 0:
            return None
            
        for group in result:
            group["subgroups"] = self.recursion(
                main_group=group, all_groups=all_groups
            )

        return result

    def __repr__(self) -> str:  # pragma: no cover
        return "Group repository"
