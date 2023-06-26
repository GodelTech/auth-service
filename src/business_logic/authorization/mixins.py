from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel

    from .interfaces import HasUserRepoProtocol


class UpdateRedirectUrlMixin:
    async def _update_redirect_url(
        self: HasUserRepoProtocol,
        request_data: AuthRequestModel,
        redirect_url: str,
    ) -> str:
        if request_data.state:
            redirect_url += f"&state={request_data.state}"
        return redirect_url
