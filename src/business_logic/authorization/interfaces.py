from __future__ import annotations
from typing import Protocol, TYPE_CHECKING


if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel


# * What about _update_redirect_url?
class AuthServiceProtocol(Protocol):
    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        ...
