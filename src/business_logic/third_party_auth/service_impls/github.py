from __future__ import annotations

import json
import secrets
import time
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
        self._secret_code = secrets.token_urlsafe(32)

    async def _form_parameters_data(self, code: str):
        (
            provider_client_id,
            provider_client_secret,
            internal_redirect_uri,
        ) = await self._oidc_repo.get_credentials_by_provider_name(
            AuthProviderName.GITHUB.value
        )
        return {
            "client_id": provider_client_id,
            "client_secret": provider_client_secret,
            "redirect_uri": internal_redirect_uri,
            "code": code,
        }

    # TODO mixin
    async def _get_access_token(self, token_url: str, code: str) -> str:
        params = await self._form_parameters_data(code)
        response = await self._async_http_client.request(
            "POST",
            token_url,
            params=params,
            headers={"Accept": "application/json"},
        )
        return json.loads(response.content)["access_token"]

    # TODO add parameter for username maybe like: login | email | nickname and create mixin
    async def _get_username(self, username_type: str, code: str) -> str:
        (
            token_url,
            user_info_url,
        ) = await self._oidc_repo.get_external_links_by_provider_name(
            AuthProviderName.GITHUB.value
        )
        access_token = await self._get_access_token(token_url, code=code)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await self._async_http_client.request(
            "GET", user_info_url, headers=headers
        )
        return json.loads(response.content)[username_type]

    async def _create_user_if_not_exists(self, username: str):
        if not await self._user_repo.exists_user(username):
            provider_id = await self._oidc_repo.get_id_by_provider_name(
                name=AuthProviderName.GITHUB.value
            )
            await self._user_repo.create(
                username=username, identity_provider_id=provider_id
            )

    async def _create__grant(
        self,
        request_data: ThirdPartyAccessTokenRequestModelBase,
        username_type: str,
    ) -> None:
        client_id = request_data.state.split("!_!")[1]
        auth_code_lifetime = (
            await self._client_repo.get_auth_code_lifetime_by_client(client_id)
        )
        username = await self._get_username(username_type, request_data.code)
        await self._create_user_if_not_exists(username)
        grant_data = {
            "client_id": client_id,
            "grant_data": self._secret_code,
            "user_id": await self._user_repo.get_user_id_by_username(username),
            "grant_type": "authorization_code",
            "expiration_time": auth_code_lifetime + int(time.time()),
        }
        await self._persistent_grant_repo.create(**grant_data)

    async def _update_redirect_url(  # TODO mixin
        self,
        request_data: ThirdPartyAccessTokenRequestModelBase,
        redirect_url: str,
    ) -> str:
        if request_data.state:
            redirect_url += f"&state={request_data.state}"
        return redirect_url

    async def get_redirect_url(
        self, request_data: ThirdPartyAccessTokenRequestModelBase
    ) -> str:
        await self._state_validator(request_data.state)
        await self._create__grant(request_data, username_type="login")
        redirect_url = (
            f"{request_data.state.split('!_!')[-1]}?code={self._secret_code}"
        )
        return await self._update_redirect_url(request_data, redirect_url)


# TODO provider_name problem
