from src.business_logic.services.tokens import get_single_token

from .base import ResponseTypeHandlerBase
from .constants import TokenExpirationTime


class IdTokenTokenResponseTypeHandler(ResponseTypeHandlerBase):
    async def get_redirect_url(self, user_id: int) -> str:
        expiration_time = TokenExpirationTime.SHORT.value
        access_token = await get_single_token(
            user_id=user_id,
            client_id=self.auth_service.request_model.client_id,
            additional_data={"scopes": self.auth_service.request_model.scope},
            jwt_service=self.auth_service.jwt_service,
            expiration_time=expiration_time,
            aud=["userinfo", "introspection", "revoke"],
        )
        claims = await self.auth_service.user_repo.get_claims(user_id)
        id_token = await get_single_token(
            user_id=user_id,
            client_id=self.auth_service.request_model.client_id,
            additional_data=claims,
            jwt_service=self.auth_service.jwt_service,
            expiration_time=expiration_time,
        )
        query_params = (
            f"access_token={access_token}&token_type=Bearer&expires_in={expiration_time}"
            f"&id_token={id_token}"
        )
        redirect_url = (
            f"{self.auth_service.request_model.redirect_uri}?{query_params}"
        )
        return await self._update_redirect_url(redirect_url)
