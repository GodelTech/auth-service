from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from httpx import AsyncClient

    from src.business_logic.third_party_auth.dto import (
        ThirdPartyAccessTokenRequestModel,
    )
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        PersistentGrantRepository,
        ThirdPartyOIDCRepository,
        UserRepository,
    )


@runtime_checkable
class ThirdPartyAuthServiceProtocol(Protocol):
    """
    Protocol defining the interface for third-party authentication services.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the third-party authentication service.
        """
        ...

    async def get_redirect_url(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
    ) -> str:
        """
        Get the redirect URL for initiating the third-party authentication flow.

        Args:
            request_data: The request data for obtaining the access token.

        Returns:
            The redirect URL to redirect the user to.
        """
        ...


class ThirdPartyAuthMixinProtocol(Protocol):
    """
    Protocol defining the interface for a mixin providing common functionality to third-party authentication services.
    """

    @property
    def _oidc_repo(self) -> ThirdPartyOIDCRepository:
        """
        Get the repository for accessing third-party OIDC-related data.
        """
        ...

    @property
    def _async_http_client(self) -> AsyncClient:
        """
        Get the asynchronous HTTP client for making requests.
        """
        ...

    @property
    def _user_repo(self) -> UserRepository:
        """
        Get the repository for accessing user-related data.
        """
        ...

    @property
    def _secret_code(self) -> str:
        """
        Get the secret code for the third-party authentication service.
        """
        ...

    @property
    def _persistent_grant_repo(self) -> PersistentGrantRepository:
        """
        Get the repository for accessing persistent grant-related data.
        """
        ...

    @property
    def _client_repo(self) -> ClientRepository:
        """
        Get the repository for accessing client-related data.
        """
        ...

    async def _form_parameters_data(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        provider_name: str,
    ) -> dict[str, str]:
        """
        Form the data parameters for the access token request.

        Args:
            request_data: The request data for obtaining the access token.
            provider_name: The name of the third-party provider.

        Returns:
            A dictionary containing the data parameters.
        """
        ...

    async def _get_access_token(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        token_url: str,
        provider_name: str,
    ) -> str:
        """
        Get the access token from the third-party authentication provider.

        Args:
            request_data: The request data for obtaining the access token.
            token_url: The URL for requesting the access token.
            provider_name: The name of the third-party provider.

        Returns:
            The access token.
        """
        ...

    async def _get_username(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        username_type: str,
        provider_name: str,
    ) -> str:
        """
        Get the username from the third-party authentication provider.

        Args:
            request_data: The request data for obtaining the access token.
            username_type: The type of username to retrieve.
            provider_name: The name of the third-party provider.

        Returns:
            The username.
        """
        ...

    async def _create_user_if_not_exists(
        self, username: str, provider_name: str
    ) -> None:
        """
        Create a user if it does not already exist.

        Args:
            username: The username of the user.
            provider_name: The name of the third-party provider.
        """
        ...
