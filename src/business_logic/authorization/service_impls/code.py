from __future__ import annotations

import secrets
import time
from typing import TYPE_CHECKING

from src.business_logic.authorization.mixins import UpdateRedirectUrlMixin

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        PersistentGrantRepository,
        UserRepository,
    )


class CodeAuthService(UpdateRedirectUrlMixin):
    def __init__(
        self,
        client_validator: ValidatorProtocol,
        redirect_uri_validator: ValidatorProtocol,
        scope_validator: ValidatorProtocol,
        user_credentials_validator: ValidatorProtocol,
        persistent_grant_repo: PersistentGrantRepository,
        client_repo: ClientRepository,
        user_repo: UserRepository,
    ) -> None:
        self._client_validator = client_validator
        self._redirect_uri_validator = redirect_uri_validator
        self._scope_validator = scope_validator
        self._user_credentials_validator = user_credentials_validator
        self._client_repo = client_repo
        self._persistent_grant_repo = persistent_grant_repo
        self._user_repo = user_repo
        self._secret_code = secrets.token_urlsafe(32)

    async def _validate_request_data(self, request_data: AuthRequestModel):
        await self._client_validator(request_data.client_id)
        await self._redirect_uri_validator(
            request_data.redirect_uri, request_data.client_id
        )
        await self._scope_validator(request_data.scope, request_data.client_id)
        await self._user_credentials_validator(
            request_data.username, request_data.password
        )  # TODO create mixin for validation with methods which are common for each service?

    async def _create_grant(self, request_data: AuthRequestModel):
        auth_code_lifetime = (
            await self._client_repo.get_auth_code_lifetime_by_client(
                request_data.client_id
            )
        )
        await self._persistent_grant_repo.create(
            client_id=request_data.client_id,
            grant_type="authorization_code",
            grant_data=self._secret_code,
            user_id=(await self._user_repo.get_user_by_username(
                request_data.username
            )).id,
            expiration_time=auth_code_lifetime + int(time.time()),
            scope=request_data.scope
        )

    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        await self._validate_request_data(request_data)
        await self._create_grant(request_data)
        redirect_url = f"{request_data.redirect_uri}?code={self._secret_code}"
        return await self._update_redirect_url(request_data, redirect_url)
