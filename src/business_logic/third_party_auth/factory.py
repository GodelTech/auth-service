from __future__ import annotations

from typing import TYPE_CHECKING, Type

from src.business_logic.third_party_auth.constants import AuthProviderName
from src.business_logic.third_party_auth.errors import (
    UnsupportedThirdPartyAuthProviderError,
)
from src.business_logic.third_party_auth.validators import (
    StateValidator,
    StateValidatorBase,
)

from .interfaces import ThirdPartyAuthServiceProtocol
from .service_impls import (
    GithubAuthService,
    GitlabAuthService,
    GoogleAuthService,
    LinkedinAuthService,
    MicrosoftAuthService,
)

if TYPE_CHECKING:
    from httpx import AsyncClient

    from src.data_access.postgresql.repositories import (
        ClientRepository,
        PersistentGrantRepository,
        ThirdPartyOIDCRepository,
        UserRepository,
    )
    from sqlalchemy.ext.asyncio import AsyncSession


ProviderNameToService = dict[str, Type[ThirdPartyAuthServiceProtocol]]


class ThirdPartyAuthServiceFactory:
    """
    Factory class for creating instances of ThirdPartyAuthServiceProtocol based on the provider name.

    Usage:
    - Register provider names and corresponding service implementations before creating instances:
        ThirdPartyAuthServiceFactory._register_factory(AuthProviderName.GITHUB.value, GithubAuthService)

    - Create an instance of ThirdPartyAuthServiceFactory in presentation layer:
        factory = ThirdPartyAuthServiceFactory(
            session, client_repo, user_repo, persistent_grant_repo, oidc_repo, async_http_client
        )

    - Get a third-party authentication service instance based on the provider name in presentation layer:
        service = factory.get_service_impl(provider_name)

    - Create a provider state in presentation layer:
        await factory.create_provider_state(state)"""

    _provider_name_to_service: ProviderNameToService = {}

    def __init__(
        self,
        session: AsyncSession,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        oidc_repo: ThirdPartyOIDCRepository,
        async_http_client: AsyncClient,
    ) -> None:
        """
        Initialize the ThirdPartyAuthServiceFactory with the required dependencies.

        Args:
            session: The async SQLAlchemy session.
            client_repo: The repository for accessing client-related data.
            user_repo: The repository for accessing user-related data.
            persistent_grant_repo: The repository for accessing persistent grant-related data.
            oidc_repo: The repository for accessing third-party OIDC-related data.
            async_http_client: The HTTP client for making asynchronous requests.
        """
        self.session = session
        self._client_repo = client_repo
        self._user_repo = user_repo
        self._persistent_grant_repo = persistent_grant_repo
        self._oidc_repo = oidc_repo
        self._async_http_client = async_http_client

    @classmethod
    def _register_factory(
        cls,
        provider_name: str,
        service_impl: Type[ThirdPartyAuthServiceProtocol],
    ) -> None:
        """
        Register a service implementation for a specific provider name.

        Args:
            provider_name: The provider name for which the service implementation is registered.
            service_impl: The service implementation to register.
        """
        cls._provider_name_to_service[provider_name] = service_impl

    def get_service_impl(
        self, provider_name: str
    ) -> ThirdPartyAuthServiceProtocol:
        """
        Get the implementation of ThirdPartyAuthServiceProtocol for the specified provider name.

        Args:
            provider_name: The provider name for which to get the service implementation.

        Returns:
            An instance of ThirdPartyAuthServiceProtocol for the specified provider name.

        Raises:
            UnsupportedThirdPartyAuthProviderError: If the provided provider_name is not supported.
        """
        third_party_auth_service = self._provider_name_to_service.get(
            provider_name
        )

        if third_party_auth_service is None:
            raise UnsupportedThirdPartyAuthProviderError(
                f"'{provider_name}' provider is not supported."
            )

        return third_party_auth_service(
            state_validator=StateValidator(self._oidc_repo),
            client_repo=self._client_repo,
            user_repo=self._user_repo,
            persistent_grant_repo=self._persistent_grant_repo,
            oidc_repo=self._oidc_repo,
            async_http_client=self._async_http_client,
        )

    async def create_provider_state(self, state: str) -> None:
        """
        Create a provider state in the third-party OIDC repository after successful state validation.

        Args:
            state: The provider state to create.
        """
        await StateValidatorBase(self._oidc_repo)(state)
        await self._oidc_repo.create_state(state)


ThirdPartyAuthServiceFactory._register_factory(
    AuthProviderName.GITHUB.value, GithubAuthService
)
ThirdPartyAuthServiceFactory._register_factory(
    AuthProviderName.GITLAB.value, GitlabAuthService
)
ThirdPartyAuthServiceFactory._register_factory(
    AuthProviderName.GOOGLE.value, GoogleAuthService
)
ThirdPartyAuthServiceFactory._register_factory(
    AuthProviderName.LINKEDIN.value, LinkedinAuthService
)
ThirdPartyAuthServiceFactory._register_factory(
    AuthProviderName.MICROSOFT.value, MicrosoftAuthService
)
