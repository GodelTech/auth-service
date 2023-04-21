from __future__ import annotations

from typing import TYPE_CHECKING, Type

from src.data_access.postgresql.errors import ThirdPartyAuthProviderNameError

from .interfaces import ThirdPartyAuthServiceProtocol

if TYPE_CHECKING:
    from httpx import AsyncClient

    from src.data_access.postgresql.repositories import (
        ClientRepository,
        PersistentGrantRepository,
        ThirdPartyOIDCRepository,
        UserRepository,
    )


ProviderNameToService = dict[str, Type[ThirdPartyAuthServiceProtocol]]


class ThirdPartyAuthServiceFactory:
    _provider_name_to_service: ProviderNameToService = {}

    def __init__(
        self,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        oidc_repo: ThirdPartyOIDCRepository,
        async_http_client: AsyncClient,
    ) -> None:
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
            raise ThirdPartyAuthProviderNameError(
                f"'{provider_name.title()}' provider is not supported."
            )

        return third_party_auth_service(
            client_repo=self._client_repo,
            user_repo=self._user_repo,
            persistent_grant_repo=self._persistent_grant_repo,
            oidc_repo=self._oidc_repo,
            async_http_client=self._async_http_client,
        )

    # TODO add creating state here?
