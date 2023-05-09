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
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, role_id: int) -> bool:
        result = await self.session.execute(
            select(exists().where(Role.id == role_id))
        )
        result = result.first()
        return result[0]

    async def delete(self, role_id: int) -> None:
        if await self.exists(role_id=role_id):
            role_to_delete = await self.get_role_by_id(role_id=role_id)
            await self.session.delete(role_to_delete)
        else:
            raise ValueError

    async def get_role_by_name(self, name: str) -> Role:
        try:
            role = await self.session.execute(
                select(Role).where(Role.name == name)
            )
            role = role.first()

            return role[0]
        except:
            raise ValueError

    async def get_role_by_id(self, role_id: int) -> Role:
        try:
            role = await self.session.execute(
                select(Role).where(Role.id == role_id)
            )
            role = role.first()

            return role[0]
        except:
            raise ValueError

    async def update(self, role_id: int, name: str) -> None:
        try:
            if await self.exists(role_id=role_id):
                updates = (
                    update(Role)
                    .values(name=name)
                    .where(Role.id == role_id)
                )
                await self.session.execute(updates)
            else:
                raise ValueError
        except ValueError:
            raise ValueError
        except:
            raise DuplicationError

    async def create(self, name: str, id: Optional[int] = None) -> None:
        kwargs = params_to_dict(name=name, id=id)
        await self.session.execute(insert(Role).values(**kwargs))

    async def get_all_roles(self) -> list[Role]:
        quiery = await self.session.execute(select(Role))
        quiery = quiery.all()
        return [role[0] for role in quiery]

    def __repr__(self) -> str:  # pragma: no cover
        return "Role repository"
