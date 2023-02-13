import logging
import uuid

from fastapi import status
from sqlalchemy import delete, exists, insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors.persistent_grant import (
    PersistentGrantNotFoundError,
)
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant, PersistentGrantType

logger = logging.getLogger(__name__)


class PersistentGrantRepository(BaseRepository):
    async def create(
        self,
        client_id: str,
        grant_data: str,
        user_id: int,
        grant_type: int = 1,
        expiration_time: int = 600,
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        # persistent_grant_id =  await self.get_type_id(grant_type)
        async with session_factory() as sess:
            session = sess

            unique_key = str(uuid.uuid4())
            persistent_grant = {
                "key": unique_key,
                "client_id": client_id,
                "grant_data": grant_data,
                "expiration": expiration_time,
                "subject_id": user_id,
                "persistent_grant_type_id": grant_type,
            }
            # The sequence id number is out of sync and raises duplicate key error
            # We manually bring it back in sync
            # await session.execute(
            #     text("SELECT setval(pg_get_serial_sequence('persistent_grants', 'id'), (SELECT MAX(id) FROM persistent_grants)+1);")
            # )
            await session.execute(
                insert(PersistentGrant).values(**persistent_grant)
            )
            await session.commit()
    
    async def get_type_id(self, type_id: int) -> PersistentGrant:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(PersistentGrantType).where(
                    PersistentGrantType.id == type_id,
                )
            )
            return result.first()[0].type_of_grant
        
    async def exists(self, grant_data: str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(
                    exists().where(
                        PersistentGrant.grant_data == grant_data,
                    )
                )
            )
            result = result.first()
            return result[0]

    async def get(self, grant_type: str, data: str) -> PersistentGrant:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(PersistentGrant).where(
                    PersistentGrant.type == grant_type,
                    PersistentGrant.data == data,
                )
            )
            return result.first()[0]

    async def delete(self, grant_data: str) -> int:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.exists(grant_data=grant_data):
                grant_to_delete = await self.get(grant_data=grant_data)
                await session.delete(grant_to_delete)
                await session.commit()
                return status.HTTP_200_OK
            else:
                return status.HTTP_404_NOT_FOUND

    async def delete_persistent_grant_by_client_and_user_id(
        self, client_id: str, user_id: int
    ) -> None:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            await self.check_grant_by_client_and_user_ids(
                client_id=client_id, user_id=user_id
            )
            await session.execute(
                delete(PersistentGrant)
                .where(PersistentGrant.client_id == client_id)
                .where(PersistentGrant.subject_id == user_id)
            )
            await session.commit()
            return None

    async def check_grant_by_client_and_user_ids(
        self, client_id: str, user_id: int
    ) -> bool:
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
                raise PersistentGrantNotFoundError(
                    "Persistent grant you are looking for does not exist"
                )
            return grant[0]

    async def get_client_id_by_data(self, data: str) -> int:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            client_id = await session.execute(
                select(PersistentGrant.client_id).where(
                    PersistentGrant.data == data
                )
            )
            client_id = client_id.first()

            if client_id is None:
                raise PersistentGrantNotFoundError(
                    "Persistent grant you are looking for does not exist"
                )
            return client_id[0]
