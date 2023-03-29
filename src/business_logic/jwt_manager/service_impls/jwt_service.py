import logging
import jwt
from src.config.rsa_keys import RSAKeypair
from src.di import Container

from typing import Any, Optional


logger = logging.getLogger(__name__)


class JWTManager:
    def __init__(self, keys: RSAKeypair = Container().config().keys) -> None:
        self.algorithm = "RS256"
        self.algorithms = ["RS256"]
        self.keys = keys
    
    def encode(self, payload: dict[str, Any]) -> str:
        token = jwt.encode(
            payload=payload, key=self.keys.private_key, algorithm=self.algorithm
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
