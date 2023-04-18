from __future__ import annotations
from typing import Protocol
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.business_logic.third_party_oidc.dto import (
        ThirdPartyProviderAccessTokenRequestModelBase,
        StateRequestModel,
    )


class ThirdPartyOIDCServiceProtocol(Protocol):
    async def get_redirect_uri(
        self,
        request_data: ThirdPartyProviderAccessTokenRequestModelBase,
        provider_name: str,
    ) -> str:
        ...
