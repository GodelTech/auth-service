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
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    async def get_redirect_url(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
    ) -> str:
        ...


class ThirdPartyAuthMixinProtocol(Protocol):
    @property
    def _oidc_repo(self) -> ThirdPartyOIDCRepository:
        ...

    @property
    def _async_http_client(self) -> AsyncClient:
        ...

    @property
    def _user_repo(self) -> UserRepository:
        ...

    @property
    def _secret_code(self) -> str:
        ...

    @property
    def _persistent_grant_repo(self) -> PersistentGrantRepository:
        ...

    @property
    def _client_repo(self) -> ClientRepository:
        ...

    async def _form_parameters_data(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        provider_name: str,
    ) -> dict[str, str]:
        ...

    async def _get_access_token(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        token_url: str,
        provider_name: str,
    ) -> str:
        ...

    async def _get_username(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        username_type: str,
        provider_name: str,
    ) -> str:
        ...

    async def _create_user_if_not_exists(
        self, username: str, provider_name: str
    ) -> None:
        ...
