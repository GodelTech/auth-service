from __future__ import annotations

from typing import TYPE_CHECKING

from src.business_logic.authorization.mixins import UpdateRedirectUrlMixin

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.data_access.postgresql.repositories import (
        PersistentGrantRepository,
        UserRepository,
    )


class TokenAuthService:
    def __init__(
        self,
        client_validator: ValidatorProtocol,
        redirect_uri_validator: ValidatorProtocol,
        scope_validator: ValidatorProtocol,
        user_credentials_validator: ValidatorProtocol,
    ) -> None:
        self._client_validator = client_validator
        self._redirect_uri_validator = redirect_uri_validator
        self._scope_validator = scope_validator
        self._user_credentials_validator = user_credentials_validator

    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        ...
