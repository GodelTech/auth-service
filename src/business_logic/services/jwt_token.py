import logging
import jwt

from src.di import Container
from src.config.rsa_keys import RSAKeypair


logger = logging.getLogger("is_app")


class JWTService:
    def __init__(self, keys: RSAKeypair = Container().config().keys) -> None:
        self.algorithm = "RS256"
        self.algorithms = ["RS256"]
        self.keys = keys

    async def encode_jwt(self, payload: dict = {}, secret: None = None) -> str:
        token = jwt.encode(
            payload=payload, 
            key=self.keys.private_key, 
            algorithm=self.algorithm
        )
        
        logger.info(f"Created token.")

        return token

    async def decode_token(self, token: str, secret: None = None) -> dict:
        token = token.replace("Bearer ", "")
        
        decoded = jwt.decode(
            token,
            key=self.keys.public_key,
            algorithms=self.algorithms
        )

        return decoded
