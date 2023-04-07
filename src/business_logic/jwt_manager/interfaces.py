from src.business_logic.jwt_manager.dto import (
    AccessTokenPayload, 
    RefreshTokenPayload, 
    IdTokenPayload,
)
from typing import Protocol, Any, Union


Payload = Union[AccessTokenPayload, RefreshTokenPayload, IdTokenPayload]


class JWTManagerProtocol(Protocol):
    def encode(self, payload: Payload, algorithm: str) -> str:
        raise NotImplementedError
    
    def decode(self, token: str, audience: str,**kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError
