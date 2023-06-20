from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.repositories import RSAKeysRepository
from src.config.rsa_keys.rsa_keys_service import RSAKeysService, RSA_keys


def provide_rsa_keys_stub() -> None:
    ...


def provide_rsa_keys(session: AsyncSession) -> RSA_keys:
    rsa_keys = RSAKeysService(
        session=session,
        rsa_keys_repo=RSAKeysRepository(session=session)
    ).get_rsa_keys()
    return rsa_keys

class ProvideRSAKeys:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __call__(self) -> RSA_keys:
        rsa_keys = await RSAKeysService(
            session=self._session,
            rsa_keys_repo=RSAKeysRepository(session=self._session)
        ).get_rsa_keys()

        return rsa_keys