import datetime
import uuid

from sqlalchemy import insert

from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.repositories.base import BaseRepository


class PersistentGrantRepository(BaseRepository):

    async def create_new_grant(self, client_id: str, secret_code: str, user_id: int) -> None:
        unique_key = str(uuid.uuid4())
        persistent_grant = {
            'key': unique_key,
            'client_id': client_id,
            'data': secret_code,
            'expiration': (datetime.datetime.now()+datetime.timedelta(seconds=3600)),
            'subject_id': user_id,
            'type': 'code'
        }
        await self.session.execute(insert(PersistentGrant).values(**persistent_grant))
        await self.session.commit()
        return
