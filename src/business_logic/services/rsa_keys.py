from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.di.providers import provide_async_session_stub
from src.data_access.postgresql.repositories.rsa_keys import RSAKeysRepository


class RSAKeysService:

    def __init__(
            self,
            session: AsyncSession = Depends(provide_async_session_stub),
    ) -> None:
        self.rsa_keys_repository = RSAKeysRepository(session)

    async def get_rsa_keys(self):
        if self.rsa_keys_repository.validate_keys_exists():
            self.rsa_keys = self.rsa_keys_repository.get_keys_from_repository()
        else:
            self.rsa_keys = self.rsa_keys_repository.generate_new_keys()
        return self.rsa_keys
