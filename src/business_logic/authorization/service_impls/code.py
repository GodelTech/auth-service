from __future__ import annotations
from typing import TYPE_CHECKING
from src.business_logic.authorization.mixins import CreateGrantMixin
import secrets

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.data_access.postgresql.repositories import (
        PersistentGrantRepository,
        UserRepository,
    )


class CodeAuthService(CreateGrantMixin):
    def __init__(
        self,
        client_validator: ValidatorProtocol,
        redirect_uri_validator: ValidatorProtocol,
        scope_validator: ValidatorProtocol,
        user_credentials_validator: ValidatorProtocol,
        persistent_grant_repo: PersistentGrantRepository,
        user_repo: UserRepository,
    ) -> None:
        self._client_validator = client_validator
        self._redirect_uri_validator = redirect_uri_validator
        self._scope_validator = scope_validator
        self._user_credentials_validator = user_credentials_validator
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
        )

    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        await self._validate_request_data(request_data)
        await self.create_grant(self._secret_code, request_data)
        return f"{request_data.redirect_uri}?code={self._secret_code}"
        # * add state feature
