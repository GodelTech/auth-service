
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.repositories.base import BaseRepository


class PersistentGrantRepository(BaseRepository):

    async def create_new_grant(self, client_id: str, secret_code: str):
        pass
