import asyncio
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.ext.asyncio import AsyncSession

from src.di.providers.rsa_keys import provide_rsa_keys
from src.config.rsa_keys import RSAKeypair
from src.business_logic.jwt_manager import JWTManager
from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol


def provide_jwt_manager_stub() -> None:
    ...


# def provide_jwt_manager(keys: RSAKeypair) -> JWTManagerProtocol:
#     return JWTManager(keys=keys)


async def provide_jwt_manager(session: AsyncSession) -> JWTManagerProtocol:
    keys = await provide_rsa_keys(session=session)
    return JWTManager(keys=keys)