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
        cls._provider_name_to_service[provider_name] = service_impl

    def get_service_impl(
        self, provider_name: str
    ) -> ThirdPartyAuthServiceProtocol:
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
