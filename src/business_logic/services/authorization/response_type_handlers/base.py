from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.business_logic.services.authorization.authorization_service import (
        AuthorizationService,
    )


class ResponseTypeHandlerBase:
    def __init__(self, auth_service: AuthorizationService) -> None:
        self.auth_service = auth_service

    async def _update_redirect_url(self, redirect_url: str) -> str:
        if self.auth_service.request_model.state:
            redirect_url += f"&state={self.auth_service.request_model.state}"
        return redirect_url
