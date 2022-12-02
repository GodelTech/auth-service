import datetime
import uuid

from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.repositories.base import BaseRepository


class PersistentGrantRepository(BaseRepository):

    async def create_new_grant(self, client_id: str, secret_code: str):
        unique_key = str(uuid.uuid4())
        persistent_grant = PersistentGrant(
            key=unique_key,
            client_id=client_id,
            data=secret_code,
            expiration=(datetime.datetime.now()),
            subject_id=2323,
            type='example'
        )
        self.session.add(persistent_grant)
        await self.session.commit()
        return
