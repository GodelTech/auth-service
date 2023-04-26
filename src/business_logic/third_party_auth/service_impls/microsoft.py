from __future__ import annotations

import json
import secrets
from typing import TYPE_CHECKING

from business_logic.third_party_auth.service_impls.mixins import (
    ThirdPartyAuthMixin,
)
from src.business_logic.third_party_auth.errors import (
    ThirdPartyAuthProviderInvalidRequestDataError,
)

from src.business_logic.third_party_auth.constants import (
    AuthProviderName,
    StateData,
)

if TYPE_CHECKING:
    from httpx import AsyncClient

    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.business_logic.third_party_auth.dto import (
        ThirdPartyAccessTokenRequestModel,
    )
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        PersistentGrantRepository,
        ThirdPartyOIDCRepository,
        UserRepository,
    )


class MicrosoftAuthService(ThirdPartyAuthMixin):
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

    async def _get_access_token(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        token_url: str,
        provider_name: str,
    ) -> str:
        params = await self._form_parameters_data(request_data, provider_name)
        response = await self._async_http_client.request(
            "POST",
            token_url,
            data=params,
            headers={"Accept": "application/json"},
        )
        error_response = json.loads(response.content).get("error")
        if error_response:
            raise ThirdPartyAuthProviderInvalidRequestDataError(error_response)

        return json.loads(response.content)["access_token"]

    async def get_redirect_url(
        self, request_data: ThirdPartyAccessTokenRequestModel
    ) -> str:
        await self._state_validator(request_data.state)
        await self._create__grant(
            request_data,
            username_type="email",
            provider_name=AuthProviderName.MICROSOFT.value,
        )
        redirect_url = f"{request_data.state.split('!_!')[StateData.REDIRECT_URL.value]}?code={self._secret_code}"
        return await self._update_redirect_url(request_data, redirect_url)
