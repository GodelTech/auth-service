from typing import Protocol
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from src.business_logic.get_tokens.dto import (
        RequestTokenModel, 
        ResponseTokenModel,
    )


class TokenServiceProtocol(Protocol):
    async def get_tokens(self, request_data: 'RequestTokenModel') -> 'ResponseTokenModel':
        raise NotImplementedError
