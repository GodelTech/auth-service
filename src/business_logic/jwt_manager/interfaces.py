from typing import Protocol, Any


class JWTManagerProtocol(Protocol):
    def encode(self) -> None:
        raise NotImplementedError
    
    def decode(self, token: str, audience: str,**kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError
