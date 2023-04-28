from typing import Any, Dict, Optional, Union

from sqlalchemy import exists, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors.user import DuplicationError
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import Role


def params_to_dict(**kwargs: Any) -> Dict[str, Any]:
    result = {}
    for key in kwargs:
        if kwargs[key] is not None:
            result[key] = kwargs[key]
    return result


class RoleRepository():
    async def exists(self, role_id: int, session: AsyncSession) -> bool:
        result = await session.execute(
            select(exists().where(Role.id == role_id))
        )
        result = result.first()
        return result[0]

    async def delete(self, role_id: int, session: AsyncSession) -> None:
        if await self.exists(role_id=role_id):
            role_to_delete = await self.get_role_by_id(role_id=role_id)
            await session.delete(role_to_delete)
            await session.commit()
        else:
            raise ValueError

    async def get_role_by_name(self, name: str, session: AsyncSession) -> Role:
        try:
            role = await session.execute(
                select(Role).where(Role.name == name)
            )
            role = role.first()

            return role[0]
        except:
            raise ValueError

    async def get_role_by_id(self, role_id: int, session: AsyncSession) -> Role:
        try:
            role = await session.execute(
                select(Role).where(Role.id == role_id)
            )
            role = role.first()

            return role[0]
        except:
            raise ValueError

    async def update(self, role_id: int, name: str, session: AsyncSession) -> None:
        try:
            if await self.exists(role_id=role_id):
                updates = (
                    update(Role)
                    .values(name=name)
                    .where(Role.id == role_id)
                )
                await session.execute(updates)
                await session.commit()
            else:
                raise ValueError
        except ValueError:
            raise ValueError
        except:
            raise DuplicationError

    async def create(self, session: AsyncSession, name: str, id: Optional[int] = None) -> None:
        kwargs = params_to_dict(name=name, id=id)
        await session.execute(insert(Role).values(**kwargs))

    async def get_all_roles(self, session: AsyncSession) -> list[Role]:
        quiery = await session.execute(select(Role))
        quiery = quiery.all()
        return [role[0] for role in quiery]

    def __repr__(self, session: AsyncSession) -> str:  # pragma: no cover
        return "Role repository"
