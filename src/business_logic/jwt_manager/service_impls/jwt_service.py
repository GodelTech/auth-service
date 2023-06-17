from __future__ import annotations
import logging
import jwt
from typing import Any, Optional, Union
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from src.config.rsa_keys import RSAKeypair
from src.di import Container
from src.business_logic.jwt_manager.dto import (
    AccessTokenPayload,
    RefreshTokenPayload,
    IdTokenPayload,
)
from src.di.providers import provide_async_session_stub
from src.data_access.postgresql.repositories import RSAKeysRepository
from data_access.postgresql.tables.rsa_keys import RSA_keys



logger = logging.getLogger(__name__)


Payload = Union[AccessTokenPayload, RefreshTokenPayload, IdTokenPayload]

class RSAKeysService:

    def __init__(
            self,
            keys: RSAKeypair = Container().config().keys,
            session: AsyncSession = Depends(provide_async_session_stub),
    ) -> None:
        self.keys = keys
        self.rsa_keys_repository = RSAKeysRepository(session)

    async def get_rsa_keys(self):
        if await self.rsa_keys_repository.validate_keys_exists():
            self.rsa_keys = await self.rsa_keys_repository.get_keys_from_repository()
        else:
            self.rsa_keys = self.keys
        return self.rsa_keys

# async def get_rsa_keys() -> RSA_keys:
#     return await RSAKeysService().get_rsa_keys()

# def get_rsa_keys() -> RSA_keys:
#     return asyncio.run(RSAKeysService().get_rsa_keys())

# KEYS = asyncio.run(RSAKeysService().get_rsa_keys())
# KEYS = await get_rsa_keys()


class JWTManager:
    def __init__(
            self,
            # keys: RSAKeypair = Container().config().keys,
            keys = RSAKeysService().get_rsa_keys()
    ) -> None:
        self.keys = keys
        print(f"jwt_service.py; keys: {self.keys}")

    def encode(self, payload: Payload, algorithm: str, secret: Optional[str] = None) -> str:
        if secret:
            key = secret
        else:
            key = self.keys.private_key

        token = jwt.encode(
            payload=payload.dict(exclude_none=True), key=key, algorithm=algorithm
        )
        return token

    def decode(self, token: str, audience: Optional[str] = None, **kwargs: Any) -> dict[str, Any]:
        token = token.replace("Bearer ", "")
        if audience:
            decoded_info = jwt.decode(token, key=self.keys.public_key, algorithms=self.algorithms,
                                      audience=audience, **kwargs,)
        else:
            decoded_info = jwt.decode(token, key=self.keys.public_key, algorithms=self.algorithms,
                                      **kwargs,)

        return decoded_info
