from sqlalchemy import select, exists, insert, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.group import *
from src.data_access.postgresql.errors.user import DuplicationError
from typing import Union

def params_to_dict(**kwargs):
    result = {}
    for key in kwargs:
        if kwargs[key] is not None:
            result[key] = kwargs[key]
    return result


class GroupRepository(BaseRepository):

    async def create(self, name:str = None, parent_group: int = None, id:int = None) -> None:
        try:
            kwargs = params_to_dict(name=name, parent_group=parent_group, id = id)
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess

                await session.execute(
                    insert(Group).values(**kwargs)
                )
                await session.commit()
        except:
            raise DuplicationError

    async def delete(self, group_id: int = None) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if group_id is None:
                await session.execute(text("TRUNCATE TABLE groups RESTART IDENTITY CASCADE"))
                await session.commit()
            elif await self.exists(group_id=group_id):
                client_to_delete = await self.get_by_id(group_id=group_id)
                await session.delete(client_to_delete)
                await session.commit()
            else:
                raise ValueError
    
    async def exists(self, group_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(
                    exists().where(Group.id == group_id)
                )
            )
            result = result.first()
            return result[0]

    async def get_by_id(self, group_id: int) -> Group:
        try:
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess

                result = await session.execute(
                    select(Group).where(
                        Group.id == group_id,
                    )
                )
                return result.first()[0]
        except:
            raise ValueError
    
    async def get_group_by_name(self, name: str) -> Group:
        
        try:
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess
                group = await session.execute(
                    select(Group).where(Group.name == name)
                )
                group = group.first()

                return group[0]
        except:
            raise ValueError

    async def get_all_groups(self) -> list:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            groups = await session.execute(
                select(Group)
            )
            result = [group[0] for group in groups]

            return result

    async def update(self, group_id: int, name:str = None, parent_group: int = None):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            kwargs = params_to_dict(name=name, parent_group=parent_group)
            async with session_factory() as sess:
                session = sess
                if await self.exists(group_id=group_id):
                    updates = update(Group).values(
                        **kwargs).where(Group.id == group_id)
                    await session.execute(updates)
                    await session.commit()
                else:
                    raise ValueError
        except:
            raise DuplicationError

    async def get_all_subgroups(self, main_group: Group) -> dict:
        all_groups = await self.get_all_groups()

        result = {f"subgroups_of_{main_group.name}_id_{main_group.id}": self.recursion(
            main_group=main_group.dictionary(), all_groups=all_groups)}
        return result

    def recursion(self, main_group: dict, all_groups: list) -> Union[list, None]:
        result = []
        groups_remove = []
        for group in all_groups:
            if main_group["id"] == group.parent_group:
                result.append(group.dictionary() | {"subgroups": ...})
                groups_remove.append(group)

        for group in groups_remove:
            all_groups.remove(group)

        if len(result) == 0:
            result = None
            return result

        for group in result:
            group["subgroups"] = self.recursion(main_group=group, all_groups=all_groups)

        return result

    def __repr__(self) -> str:
        return "Group repository"