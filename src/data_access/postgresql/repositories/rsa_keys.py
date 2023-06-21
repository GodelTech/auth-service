# from Crypto.PublicKey import RSA
from sqlalchemy import exists, select, insert

from src.config.rsa_keys import CreateRSAKeypair, RSAKeypair
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.rsa_keys import RSA_keys


class RSAKeysRepository(BaseRepository):

    async def get_keys_from_repository(self) -> RSA_keys:
        result = await self.session.execute(select(RSA_keys))
        rsa_keys_list = result.scalars().all()
        return rsa_keys_list[-1] if len(rsa_keys_list) > 0 else None

    async def put_keys_to_repository(self, rsa_keys) -> None:
        await self.session.execute(insert(RSA_keys).values(
            private_key=rsa_keys.private_key,
            public_key=rsa_keys.public_key,
            n=rsa_keys.n,
            e=rsa_keys.e
        )
        )
        await self.session.commit()

    async def validate_keys_exists(self) -> bool:
        result = await self.session.execute(
            select([1]).where(exists().where(RSA_keys.id != None))
        )
        return result.scalars().first() is not None

