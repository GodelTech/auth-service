from __future__ import annotations
import logging
import jwt
from typing import Any, Optional, Union

from src.data_access.postgresql.tables.rsa_keys import RSA_keys
from src.business_logic.jwt_manager.dto import (
    AccessTokenPayload,
    RefreshTokenPayload,
    IdTokenPayload,
)

logger = logging.getLogger(__name__)

Payload = Union[AccessTokenPayload, RefreshTokenPayload, IdTokenPayload]

class JWTManager:
    def __init__(
            self,
            keys: RSA_keys
    ) -> None:
        self.algorithm = "RS256"
        self.algorithms = ["RS256"]
        self.keys = keys
        print(f"print:!!!jwt_service.py;!!! self.keys: {self.keys}")

    async def encode(self, payload: Payload, algorithm: str, secret: Optional[str] = None) -> str:
        if secret:
            key = secret
        else:
            key = self.keys.private_key
            print(f"jwt_service.py; keys: {self.keys.private_key}")

        token = jwt.encode(
            payload=payload.dict(exclude_none=True), key=key, algorithm=algorithm
        )
        return token

    async def decode(self, token: str, audience: Optional[str] = None, **kwargs: Any) -> dict[str, Any]:
        token = token.replace("Bearer ", "")
        if audience:
            decoded_info = jwt.decode(token, key=self.keys.public_key, algorithms=self.algorithms,
                                      audience=audience, **kwargs,)
            print(f"!!!!!!!!decoded_info: {decoded_info}")
        else:
            decoded_info = jwt.decode(token, key=self.keys.public_key, algorithms=self.algorithms,
                                      **kwargs,)

        return decoded_info

    async def verify_token(self, token: str, aud: str = None) -> bool:
        try:
            if aud:
                await self.decode(token=token, audience=aud)
            else:
                await self.decode(token)
            return True
        except:
            return False

    async def get_module(self) -> int:
        return self.keys.n

    async def get_pub_key_expanent(self) -> int:
        return self.keys.e
