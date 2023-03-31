from typing import TYPE_CHECKING
import secrets

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.business_logic.common.interfaces import ValidatorProtocol


class CodeAuthService:
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

    async def _validate_request_data(self, request_data: AuthRequestModel):
        await self._client_validator(request_data.client_id)
        await self._redirect_uri_validator(request_data.redirect_uri)
        await self._scope_validator(request_data.scope)
        await self._user_credentials_validator(
            request_data.username, request_data.password
        )

    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        await self._validate_request_data(request_data)
        return "https://www.google.com/"
