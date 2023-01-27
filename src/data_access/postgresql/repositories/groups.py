from sqlalchemy import select, exists, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import status
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.group import *


class GroupRepository(BaseRepository):

    async def create(
        self,
        **kwargs
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            await session.execute(
                insert(Group).values(**kwargs)
            )
            await session.commit()

    async def delete(self, group_id:int = None) -> int:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if group_id is None:
                await session.execute("TRUNCATE TABLE groups RESTART IDENTITY CASCADE")
                await session.commit()
            elif await self.exists(group_id=group_id):
                client_to_delete = await self.get_by_id(group_id=group_id)
                await session.delete(client_to_delete)
                await session.commit()
                return status.HTTP_200_OK
            else:
                return status.HTTP_404_NOT_FOUND
    
    async def exists(self, group_id:int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(
                    [
                        exists().where(
                            Group.id == group_id
                        )
                    ]
                )
            )
            result = result.first()
            return result[0]

    async def get_by_id(self, group_id:int) -> Group:
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

    async def get_all_subgroups(self, main_group: Group) -> dict:
        all_groups = await self.get_all_groups()

        result = {main_group: self.recursion(
            main_group=main_group, all_groups=all_groups)}
        return result

    def recursion(self, main_group:Group, all_groups:list) -> list:
        result = []
        groups_remove = []
        for group in all_groups:
            if main_group.id == group.parent_group:
                result.append({group: ...})
                groups_remove.append(group)

        for group in groups_remove:
            all_groups.remove(group)

        if len(result) == 0:
            result = None
            return result

        for group in result:
            key = list(group.keys())[0]
            group[key] = self.recursion(main_group=key, all_groups=all_groups)

        return result

    def __repr__(self) -> str:
        return "Group repository"
