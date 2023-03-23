import secrets

from src.business_logic.services.authorization.response_type_handlers.base import (
    ResponseTypeHandlerBase,
)


class CodeResponseTypeHandler(ResponseTypeHandlerBase):
    async def get_redirect_url(self, user_id: int) -> str:
        secret_code = secrets.token_urlsafe(32)
        await self.auth_service.persistent_grant_repo.create(
            client_id=self.auth_service.request_model.client_id,
            grant_data=secret_code,
            user_id=user_id,
        )
        redirect_url = f"{self.auth_service.request_model.redirect_uri}?code={secret_code}"
        return await self._update_redirect_url(redirect_url)
