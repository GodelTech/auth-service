from typing import Protocol
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from src.business_logic.get_tokens.dto import (
        RequestTokenModel, 
        ResponseTokenModel,
    )


class TokenServiceProto(Protocol):
    async def get_tokens(request_data: 'RequestTokenModel') -> 'ResponseTokenModel':
        raise NotImplementedError
