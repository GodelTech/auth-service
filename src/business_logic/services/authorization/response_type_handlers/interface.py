from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.business_logic.services.authorization.authorization_service import (
        AuthorizationService,
    )


class IResponseTypeHandler(Protocol):
    def __init__(self, auth_service: AuthorizationService) -> None:
        ...

    async def get_redirect_url(self, user_id: int) -> str:
        ...

    async def _update_redirect_url(self, redirect_url: str) -> str:
        ...
