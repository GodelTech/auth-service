from __future__ import annotations
import logging
import jwt
from typing import Any, Optional, Union
from fastapi import Depends

from src.config.rsa_keys import RSAKeypair
from src.di import Container
from src.business_logic.jwt_manager.dto import (
    AccessTokenPayload,
    RefreshTokenPayload,
    IdTokenPayload,
)
from src.di.providers.rsa_keys import provide_rsa_keys_stub

logger = logging.getLogger(__name__)


Payload = Union[AccessTokenPayload, RefreshTokenPayload, IdTokenPayload]




class JWTManager:
    def __init__(
            self,
            # keys: RSAKeypair = Container().config().keys,
            keys: RSAKeypair
            # keys = RSAKeysService().get_rsa_keys()
    ) -> None:
        self.keys = keys
        print(f"jwt_service.py; keys: {self.keys}")

    def encode(self, payload: Payload, algorithm: str, secret: Optional[str] = None) -> str:
        if secret:
            key = secret
        else:
            key = self.keys.private_key
            print(f"jwt_service.py; keys: {self.keys.private_key}")

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
