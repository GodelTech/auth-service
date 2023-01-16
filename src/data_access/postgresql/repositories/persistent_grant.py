import datetime
import logging
import time
import uuid
from typing import Union

from sqlalchemy import exists, insert, select

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant

logger = logging.getLogger("is_app")


class PersistentGrantRepository(BaseRepository):
    async def create(
        self,
        client_id: str,
        data: str,
        user_id: int,
        grant_type: str = "code",
        expiration_time: Union[int, datetime.datetime] = time.time(),
    ) -> None:
        unique_key = str(uuid.uuid4())
        persistent_grant = {
            "key": unique_key,
            "client_id": client_id,
            "data": data,
            "expiration": expiration_time,
            "subject_id": user_id,
            "type": grant_type,
        }
        await self.session.execute(
            insert(PersistentGrant).values(**persistent_grant)
        )
        await self.session.commit()

    async def exists(self, grant_type: str, data: str) -> bool:

        result = await self.session.execute(
            select(
                [
                    exists().where(
                        PersistentGrant.type == grant_type,
                        PersistentGrant.data == data,
                    )
                ]
            )
        )
        result = result.first()
        return result[0]

    async def get(self, grant_type: str, data: str):
        result = await self.session.execute(
            select(PersistentGrant).where(
                PersistentGrant.type == grant_type, PersistentGrant.data == data
            )
        )
        return result.first()[0]

    async def delete(self, client_id: str, data: str, grant_type: str):
        grant_to_delete = await self.get(grant_type=grant_type, data=data)
        await self.session.delete(grant_to_delete)
        await self.session.flush()

    async def get_client_id_by_data(self, data):
        client_id = await self.session.execute(
            select(PersistentGrant.client_id).where(PersistentGrant.data == data)
        )
        client_id = client_id.first()

        if client_id is None:
            raise Exception( # add persistent grant error
                "Persistent grant you are looking for does not exist"
            )
        return client_id[0]
