import logging

import jwt
from typing import Any, no_type_check
from src.config.rsa_keys import RSAKeypair
from src.di import Container

logger = logging.getLogger(__name__)


class JWTService:
    def __init__(self, keys: RSAKeypair = Container().config().keys) -> None:
        self.algorithm = "RS256"
        self.algorithms = ["RS256"]
        self.keys = keys

    @no_type_check
    async def encode_jwt(self, payload: dict[str, Any] = {}, secret: None = None) -> str:
        token = jwt.encode(
            payload=payload, key=self.keys.private_key, algorithm=self.algorithm
        )

        logger.info(f"Created token.")

        return token

    @no_type_check
    async def decode_token(self, token: str, audience:str =None ,**kwargs:Any) -> dict[str, Any]:

        token = token.replace("Bearer ", "")
        if audience:
            decoded = jwt.decode(
                token,
                key=self.keys.public_key,
                algorithms=self.algorithms,
                audience=audience,
                **kwargs,
            )
            return decoded
        decoded = jwt.decode(
            token,
            key=self.keys.public_key,
            algorithms=self.algorithms,
            **kwargs,
        )
        return decoded

    async def verify_token(self, token: str, aud:str=None) -> bool:
        try:
            if aud:
                await self.decode_token(token=token, audience=aud)
            else:
                await self.decode_token(token)
            return True
        except:
            return False
        
    async def get_module(self) -> int:
        return self.keys.n

    async def get_pub_key_expanent(self) -> int:
        return self.keys.e
