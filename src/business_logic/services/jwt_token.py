import logging

import jwt
from typing import Any, no_type_check, Optional
from src.config.rsa_keys import RSAKeypair

logger = logging.getLogger(__name__)


class JWTService:
    def __init__(self) -> None:
        self.algorithm = "RS256"
        self.algorithms = ["RS256"]
        self.keys:Optional[RSAKeypair] = None
    
    def check_rsa_keys(self): 
        if not self.keys:
            self.keys = 123 
            if self.keys is None:
                raise ValueError("Keys don't exist or Docker is not running")

    @no_type_check
    async def encode_jwt(self, payload: dict[str, Any] = {}, secret: None = None) -> str:
        self.check_rsa_keys()
        token = jwt.encode(
            payload=payload, key=self.keys().private_key, algorithm=self.algorithm
        )

        logger.info(f"Created token.")

        return token

    @no_type_check
    async def decode_token(self, token: str, audience: str =None ,**kwargs: Any) -> dict[str, Any]:
        self.check_rsa_keys()
        token = token.replace("Bearer ", "")
        if audience:
            decoded = jwt.decode(
                token,
                key=self.keys().public_key,
                algorithms=self.algorithms,
                audience=audience,
                **kwargs,
            )
            return decoded
        decoded = jwt.decode(
            token,
            key=self.keys().public_key,
            algorithms=self.algorithms,
            **kwargs,
        )
        return decoded

    async def verify_token(self, token: str, aud:str=None) -> bool:
        self.check_rsa_keys()
        try:
            if aud:
                await self.decode_token(token=token, audience=aud)
            else:
                await self.decode_token(token)
            return True
        except:
            return False
        
    async def get_module(self) -> int:
        self.check_rsa_keys()
        return self.keys().n

    async def get_pub_key_expanent(self) -> int:
        self.check_rsa_keys()
        return self.keys().e
