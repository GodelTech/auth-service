from Crypto.PublicKey import RSA
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.repositories import RSAKeysRepository
from src.data_access.postgresql.tables.rsa_keys import RSA_keys
from .dto import RSAKeypair

class RSAKeysService:

    def __init__(
            self,
            session: AsyncSession,
            rsa_keys_repo: RSAKeysRepository
    ) -> None:
        self.rsa_keys_repo = rsa_keys_repo

    async def get_rsa_keys(self) -> RSA_keys:
        if await self.rsa_keys_repo.validate_keys_exists():
            self.rsa_keys = await self.rsa_keys_repo.get_keys_from_repository()
        else:
            self.rsa_keys = await self.create_rsa_keys()                         # RSAKeypair
            await self.rsa_keys_repo.put_keys_to_repository(self.rsa_keys)
            self.rsa_keys = await self.rsa_keys_repo.get_keys_from_repository()  # RSA_keys
        return self.rsa_keys

    async def create_rsa_keys(self) -> RSAKeypair:    # or -> RSA_keys
        key = RSA.generate(2048)
        private_key = key.export_key("PEM")
        public_key = key.public_key().export_key("PEM")

        self.rsa_keys = RSAKeypair(
            private_key=private_key,
            public_key=public_key,
            n=key.n,
            e=key.e,
        )
        return self.rsa_keys