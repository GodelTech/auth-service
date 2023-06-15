from sqlalchemy import exists, select, insert, update, delete, text

from src.config.rsa_keys import RSAKeypair
from src.data_access.postgresql.repositories.base import BaseRepository

class RSAKeysRepository(BaseRepository):

    async def get_keys(self) -> RSAKeypair:
        pass


    async def generate_keys(self) -> RSAKeypair:
        pass
