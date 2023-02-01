import logging
import uuid

from fastapi import status
from sqlalchemy import insert, delete, select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.errors.persistent_grant import PersistentGrantNotFoundError

logger = logging.getLogger("is_app")


class PersistentGrantRepository(BaseRepository):
    async def create(
        self,
        client_id: str,
        data: str,
        user_id: int,
        grant_type: str = 'code',
        expiration_time: int = 600,
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            unique_key = str(uuid.uuid4())
            persistent_grant = {
                "key": unique_key,
                "client_id": client_id,
                "data": data,
                "expiration": expiration_time,
                "subject_id": user_id,
                "type": grant_type,
            }
            await session.execute(
                insert(PersistentGrant).values(**persistent_grant)
            )
            await session.commit()

    async def exists(self, grant_type: str, data: str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(
                    exists().where(
                            PersistentGrant.type == grant_type,
                            PersistentGrant.data == data,
                        )
                    )
                )
            result = result.first()
            return result[0]

    async def get(self, grant_type: str, data: str):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(PersistentGrant).where(
                    PersistentGrant.type == grant_type, PersistentGrant.data == data
                )
            )
            return result.first()[0]

    async def delete(self, data: str, grant_type: str) -> int:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.exists(grant_type=grant_type, data=data):
                grant_to_delete = await self.get(grant_type=grant_type, data=data)
                await session.delete(grant_to_delete)
                await session.commit()
                return status.HTTP_200_OK
            else:
                return status.HTTP_404_NOT_FOUND

    async def delete_persistent_grant_by_client_and_user_id(
            self,
            client_id: str,
            user_id: int
            ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            await self.check_grant_by_client_and_user_ids(client_id=client_id, user_id=user_id)
            await session.execute(
                delete(PersistentGrant).
                where(PersistentGrant.client_id == client_id).
                where(PersistentGrant.subject_id == user_id)
            )
            await session.commit()
            return None

    async def check_grant_by_client_and_user_ids(self, client_id: str, user_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            grant = await session.execute(
                select(
                        exists().where(
                            PersistentGrant.client_id == client_id,
                            PersistentGrant.subject_id == user_id,
                        )
                    )
                )
            grant = grant.first()
            if not grant[0]:
                raise PersistentGrantNotFoundError('Persistent grant you are looking for does not exist')
            return grant[0]

    async def get_client_id_by_data(self, data):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            client_id = await session.execute(
                select(PersistentGrant.client_id).where(PersistentGrant.data == data)
            )
            client_id = client_id.first()

            if client_id is None:
                raise PersistentGrantNotFoundError(
                    "Persistent grant you are looking for does not exist"
                )
            return client_id[0]
