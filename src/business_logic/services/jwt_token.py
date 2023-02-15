import logging
from typing import Any, Dict, Optional, Union

import jwt

from src.config.rsa_keys import RSAKeypair
from src.di import Container

logger = logging.getLogger(__name__)


class JWTService:
    def __init__(self, keys: RSAKeypair = Container().config().keys) -> None:
        self.algorithm = "RS256"
        self.algorithms = ["RS256"]
        self.keys = keys

    async def encode_jwt(
        self, payload: Optional[Dict[str, Any]] = {}, secret: None = None
    ) -> str:
        token = jwt.encode(
            payload=payload, key=self.keys.private_key, algorithm=self.algorithm
        )

        logger.info(f"Created token.")

        return token

    async def decode_token(self, token: str, **kwargs: Any) -> Dict[str, Any]:
        token = token.replace("Bearer ", "")
        decoded = jwt.decode(
            token,
            key=self.keys.public_key,
            algorithms=self.algorithms,
            **kwargs,
        )
        return decoded

    async def verify_token(self, token: str) -> bool:
        return bool(await self.decode_token(token))

    async def get_module(self) -> Union[int, float]:
        return self.keys.n

    async def get_pub_key_exponent(self) -> float:
        return self.keys.e
