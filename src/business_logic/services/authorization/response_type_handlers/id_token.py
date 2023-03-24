from src.business_logic.services.tokens import get_single_token

from .base import ResponseTypeHandlerBase
from .constants import TokenExpirationTime


class IdTokenResponseType(ResponseTypeHandlerBase):
    async def get_redirect_url(self, user_id: int) -> str:
        claims = await self.auth_service.user_repo.get_claims(user_id)
        id_token = await get_single_token(
            user_id=user_id,
            client_id=self.auth_service.request_model.client_id,
            additional_data=claims,
            jwt_service=self.auth_service.jwt_service,
            expiration_time=TokenExpirationTime.SHORT.value,
        )
        redirect_url = f"{self.auth_service.request_model.redirect_uri}?id_token={id_token}"
        return await self._update_redirect_url(redirect_url)
