from __future__ import annotations

from typing import TYPE_CHECKING

from ..constants import AuthProviderName

if TYPE_CHECKING:
    from httpx import AsyncClient

    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.business_logic.third_party_auth.dto import (
        StateRequestModel,
        ThirdPartyAccessTokenRequestModelBase,
    )
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        PersistentGrantRepository,
        ThirdPartyOIDCRepository,
        UserRepository,
    )


class GithubAuthService:
    def __init__(
        self,
        state_validator: ValidatorProtocol,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        oidc_repo: ThirdPartyOIDCRepository,
        async_http_client: AsyncClient,
    ) -> None:
        self._state_validator = state_validator
        self._client_repo = client_repo
        self._user_repo = user_repo
        self._persistent_grant_repo = persistent_grant_repo
        self._oidc_repo = oidc_repo
        self._async_http_client = async_http_client

    async def get_redirect_uri(
        self, request_data: ThirdPartyAccessTokenRequestModelBase
    ):
        await self._state_validator(request_data.state)
        (
            token_url,
            user_info_url,
        ) = await self._oidc_repo.get_external_links_by_provider_name(
            AuthProviderName.GITHUB.value
        )
