from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

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

    async def _get_access_token(self, token_url: str) -> str:  # TODO mixin
        params = "todo"  # TODO
        response = await self._async_http_client.request(
            "POST",
            token_url,
            params=params,
            headers={"Accept": "application/json"},
        )
        return json.loads(response.content)["access_token"]

    async def _get_username(  # TODO add parameter for username maybe like: login | email | nickname and create mixin
        self, user_data_url: str, access_token: str
    ) -> str:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await self._async_http_client.request(
            "GET", user_data_url, headers=headers
        )
        return json.loads(response.content)["login"]

    async def get_redirect_uri(
        self, request_data: ThirdPartyAccessTokenRequestModelBase
    ):
        await self._state_validator(request_data.state)

        # TODO extract it to some function
        (
            token_url,
            user_info_url,
        ) = await self._oidc_repo.get_external_links_by_provider_name(
            AuthProviderName.GITHUB.value
        )

        access_token = await self._get_access_token(token_url)
        username = await self._get_username(user_info_url, access_token)
