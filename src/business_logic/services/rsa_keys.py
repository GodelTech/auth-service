from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.repositories import RSAKeysRepository


class RSAKeysService:

    def __init__(
            self,
            rsa_keys: RSAKeysRepository,
            session: AsyncSession
    ) -> None:
        self.rsa_keys = rsa_keys
        self.session = session

    def __call__(self, *args, **kwargs):
        pass
