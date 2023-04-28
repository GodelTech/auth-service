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


class GroupRepository():
    async def create(
        self, session: AsyncSession, name: str, parent_group: Optional[int] = None, id: Optional[int] = None
    ) -> None:
        try:
            kwargs = params_to_dict(
                name=name, parent_group=parent_group, id=id
            )
            await session.execute(insert(Group).values(**kwargs))
                # await session.commit()
        except Exception as e:
            raise DuplicationError(e)

    async def delete(self, session: AsyncSession, group_id: Optional[int] = None) -> None:

        if group_id is None:
            await session.execute(text("DELETE FROM groups"))
        elif await self.exists(session=session, group_id=group_id):
            client_to_delete = await self.get_by_id(session=session, group_id=group_id)
            await session.delete(client_to_delete)
        else:
            raise ValueError

    async def exists(self, group_id: int, session: AsyncSession,) -> bool:

        result = await session.execute(
            select(exists().where(Group.id == group_id))
        )
        result = result.first()
        return result[0]

    async def get_by_id(self, group_id: int, session: AsyncSession,) -> Group:
        try:
            result = await session.execute(
                select(Group).where(
                    Group.id == group_id,
                )
            )
            return result.first()[0]
        except Exception as e:
            raise e

    async def get_group_by_name(self, name: str, session: AsyncSession,) -> Group:
        try:
            group = await session.execute(
                select(Group).where(Group.name == name)
            )
            group = group.first()

            return group[0]
        except:
            raise ValueError

    async def get_all_groups(self, session: AsyncSession,) -> list[Group]:
        groups = await session.execute(select(Group))
        result = [group[0] for group in groups]

        return result

    async def update(
        self, session: AsyncSession, group_id: int, name: Optional[str] = None, parent_group: Optional[int] = None
    ) -> None:
        try:
            kwargs = params_to_dict(name=name, parent_group=parent_group)
            if await self.exists(session=session, group_id=group_id):
                updates = (
                    update(Group)
                    .values(**kwargs)
                    .where(Group.id == group_id)
                )
                await session.execute(updates)
            else:
                raise ValueError

        except ValueError:
            raise ValueError
        except Exception as e:
            raise DuplicationError(e)

    async def get_all_subgroups(self, main_group: Group, session: AsyncSession) -> dict[str, Any]:
        all_groups = await self.get_all_groups(session=session)

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
