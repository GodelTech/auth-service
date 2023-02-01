from sqlalchemy import select, exists, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import Role
from src.data_access.postgresql.errors.user import DuplicationError


class RoleRepository(BaseRepository):
    async def exists(self, role_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(exists().where(Role.id == role_id))
            )
            result = result.first()
            return result[0]

    async def delete(self, role_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.exists(role_id=role_id):
                role_to_delete = await self.get_role_by_id(role_id=role_id)
                await session.delete(role_to_delete)
                await session.commit()
                return True
            else:
                raise ValueError

    async def get_role_by_id(self, role_id: int) -> Role:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                role = await session.execute(
                    select(Role).where(Role.id == role_id)
                )
                role = role.first()

                return role[0]
        except:
            raise ValueError
            
    async def update(self, role_id: int, **kwargs) -> bool:

        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.exists(role_id=role_id):
                updates = update(Role).values(
                    **kwargs).where(Role.id == role_id)
                await session.execute(updates)
                await session.commit()
                return True
            else:
                return False

    async def create(self, **kwargs) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess

                await session.execute(
                    insert(Role).values(**kwargs)
                )
                await session.commit()
                return True
        except:
            raise DuplicationError

    async def get_all_roles(self) -> list[Role]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        async with session_factory() as sess:
            session = sess

            quiery = await session.execute(
                select(Role)
            )
            quiery = quiery.all()
            return [role[0] for role in quiery]
    
    def __repr__(self) -> str:
        return "Role repository"
