from src.business_logic.jwt_manager.dto import (
    AccessTokenPayload, 
    RefreshTokenPayload, 
    IdTokenPayload,
)
from typing import Protocol, Any, Union


Payload = Union[AccessTokenPayload, RefreshTokenPayload, IdTokenPayload]


class JWTManagerProtocol(Protocol):
    async def encode(self, payload: Payload, algorithm: str) -> str:
        raise NotImplementedError
    
    async def decode(self, token: str, audience: str,**kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError
