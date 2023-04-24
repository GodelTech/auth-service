from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from src.business_logic.third_party_auth.dto import (
        StateRequestModel,
        ThirdPartyAccessTokenRequestModel,
    )


class ThirdPartyAuthServiceProtocol(Protocol):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    async def get_redirect_url(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
    ) -> str:
        ...
