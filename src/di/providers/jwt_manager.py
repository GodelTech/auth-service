from sqlalchemy.ext.asyncio import AsyncSession

# from src.di.providers.rsa_keys import ProvideRSAKeys
from src.config.rsa_keys import RSAKeypair
from src.business_logic.jwt_manager import JWTManager
from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol


def provide_jwt_manager_stub() -> None:
    ...


def provide_jwt_manager(keys: RSAKeypair) -> JWTManagerProtocol:
    return JWTManager(keys=keys)

# async def provide_jwt_manager(session: AsyncSession) -> JWTManagerProtocol:
#     keys = await ProvideRSAKeys(session=session)()
#     return JWTManager(keys=keys)