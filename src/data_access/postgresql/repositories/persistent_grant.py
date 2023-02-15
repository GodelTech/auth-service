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
from src.data_access.postgresql.tables import PersistentGrant, PersistentGrantType, Client

logger = logging.getLogger(__name__)


class PersistentGrantRepository(BaseRepository):
    async def create(
        self,
        client_id: str,
        grant_data: str,
        user_id: int,
        grant_type: str = 'code',
        expiration_time: int = 600,
    ) -> None:
        grant_type_id = await self.get_type_id(grant_type)
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        # persistent_grant_id =  await self.get_type_id(grant_type)
        async with session_factory() as sess:
            session = sess

            client_id_int = await self.get_client_id_int(client_id=client_id, session=session)
            unique_key = str(uuid.uuid4())
            persistent_grant = {
                "key": unique_key,
                "client_id": client_id_int,
                "grant_data": grant_data,
                "expiration": expiration_time,
                "user_id": user_id,
                "persistent_grant_type_id": grant_type_id,
            }

            await session.execute(
                insert(PersistentGrant).values(**persistent_grant)
            )
            await session.commit()
    
    async def get_type_id(self, type_of_grant: str) -> PersistentGrant:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(PersistentGrantType).where(
                
                    PersistentGrantType.type_of_grant == type_of_grant,
                )
            )
            return result.first()[0].id
            
    async def get_client_id(self, client_id_str: str) -> PersistentGrant:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(Client).where(
                    Client.client_id == client_id_str,
                )
            )
            return result.first()[0].id
    
    async def exists(self, grant_data: str, grant_type:str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(PersistentGrant).join(PersistentGrantType, PersistentGrantType.id == PersistentGrant.persistent_grant_type_id)
                        .where(
                        PersistentGrantType.type_of_grant == grant_type,
                        PersistentGrant.grant_data == grant_data,
                    )
                )

            result = result.first()
            return bool(result)

    async def get(self, grant_type: str, grant_data: str) -> PersistentGrant:
        
        grant_type_id = await self.get_type_id(type_of_grant = grant_type)
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(PersistentGrant).where(
                    PersistentGrant.persistent_grant_type_id == grant_type_id,
                    PersistentGrant.grant_data == grant_data,
                )
            )
            return result.first()[0]

    async def delete(self, grant_type:str, grant_data: str) -> int:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.exists(grant_data=grant_data, grant_type = grant_type):
                grant_to_delete = await self.get(grant_data=grant_data, grant_type=grant_type)
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
            client_id = await self.get_client_id_int(client_id = client_id, session=session)
            await session.execute(
                delete(PersistentGrant)
                .where(PersistentGrant.client_id == client_id,
                       PersistentGrant.user_id == user_id)
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
            client_id = await self.get_client_id_int(client_id = client_id, session=session)
            grant = await session.execute(
                select(
                    exists().where(
                        PersistentGrant.client_id == client_id,
                        PersistentGrant.user_id == user_id,
                    )
                )
            )
            grant = grant.first()
            if not grant[0]:
                raise PersistentGrantNotFoundError(
                    "Persistent grant you are looking for does not exist"
                )
            return grant[0]

    async def get_client_id_by_data(self, grant_data: str) -> int:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            client_id = await session.execute(
                select(PersistentGrant.client_id).where(
                    PersistentGrant.grant_data == grant_data
                )
            )
            client_id = client_id.first()

            if client_id is None:
                raise PersistentGrantNotFoundError(
                    "Persistent grant you are looking for does not exist"
                )
            else:
                client_id = client_id[0]

            client_id_str = await session.execute(select(Client.client_id).where(
                    Client.id == client_id,
                ))
            client_id_str = client_id_str.first()

            if client_id_str is None:
                raise PersistentGrantNotFoundError
            else:
                return client_id_str[0]

    async def get_client_id_int(self, client_id:str, session) -> int:
        client_id = await session.execute(select(Client.id).where(
                    Client.client_id == client_id,
                ))
        client_id= client_id.first()

        if client_id is None:
            raise PersistentGrantNotFoundError
        else:
            return client_id[0]