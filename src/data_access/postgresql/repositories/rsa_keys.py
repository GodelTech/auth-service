from Crypto.PublicKey import RSA
from sqlalchemy import exists, select, insert, update, delete, text

from src.config.rsa_keys import CreateRSAKeypair, RSAKeypair
# from src.config.rsa_keys import RSAKeypair
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.rsa_keys import RSA_keys


class RSAKeysRepository(BaseRepository):

    async def get_keys_from_repository(self) -> RSA_keys:
        result = await self.session.execute(
            select(RSA_keys).where(RSA_keys.id == 1)
        )
        rsa_keys = result.scalars().first()
        return rsa_keys if rsa_keys else None

    async def generate_new_keys(self) -> RSA_keys:
        rsa_keys: RSAKeypair = CreateRSAKeypair().execute()
        await self.session.execute(insert(RSA_keys).values(
            private_key=rsa_keys.private_key,
            public_key=rsa_keys.public_key,
            n=rsa_keys.n,
            e=rsa_keys.e
        )
        )
        rsa_keys = self.get_keys_from_repository()
        await self.session.commit()
        return rsa_keys
        # await self.session.refresh(new_key)
        # return new_key

    async def validate_keys_exists(self) -> bool:
        result = await self.session.execute(
            select(RSA_keys).exists().select()
        )
        return result
