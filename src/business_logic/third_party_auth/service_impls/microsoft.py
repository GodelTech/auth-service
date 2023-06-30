from __future__ import annotations

import json
import secrets
from typing import TYPE_CHECKING

from src.business_logic.third_party_auth.service_impls.mixins import (
    ThirdPartyAuthMixin,
)
from src.business_logic.third_party_auth.constants import (
    AuthProviderName,
    StateData,
)
from src.business_logic.third_party_auth.errors import (
    ThirdPartyAuthProviderInvalidRequestDataError,
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
    """
    Service class for handling authentication with Microsoft as a third-party provider.

    This class implements the necessary methods and functionality to authenticate users
    using Microsoft's OAuth 2.0 flow.

    Inherits:
        ThirdPartyAuthMixin: A mixin class providing common methods for third-party authentication.
    """

    def __init__(
        self,
        state_validator: ValidatorProtocol,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        oidc_repo: ThirdPartyOIDCRepository,
        async_http_client: AsyncClient,
    ) -> None:
        """
        Initialize a new instance of MicrosoftAuthService.

        Args:
            state_validator (ValidatorProtocol): The validator for the state parameter.
            client_repo (ClientRepository): The repository for client-related operations.
            user_repo (UserRepository): The repository for user-related operations.
            persistent_grant_repo (PersistentGrantRepository): The repository for persistent grant-related operations.
            oidc_repo (ThirdPartyOIDCRepository): The repository for OpenID Connect-related operations.
            async_http_client (AsyncClient): The asynchronous HTTP client for making HTTP requests.
        """
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
        """
        Retrieve the access token from Microsoft.

        Args:
            request_data (ThirdPartyAccessTokenRequestModel): The request data containing the authorization code and state.
            token_url (str): The URL for obtaining the access token from Microsoft.
            provider_name (str): The name of the third-party provider (Microsoft).

        Returns:
            str: The access token.

        Raises:
            ThirdPartyAuthProviderInvalidRequestDataError: If the request to Microsoft returns an error response.
        """
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
        """
        Generates the redirect URL for the Microsoft authentication flow.

        Args:
            request_data (ThirdPartyAccessTokenRequestModel): The request data containing the authorization code and state.

        Returns:
            str: The generated redirect URL.

        Raises:
            ThirdPartyAuthInvalidStateError: If the requested scope is invalid.
            ThirdPartyAuthProviderInvalidRequestDataError: If the request to Microsoft returns an error response.
        """
        await self._state_validator(request_data.state)
        await self._create_grant(
            request_data,
            username_type="email",
            provider_name=AuthProviderName.MICROSOFT.value,
        )
        redirect_url = f"{request_data.state.split('!_!')[StateData.REDIRECT_URL.value]}?code={self._secret_code}"
        return await self._update_redirect_url(request_data, redirect_url)
