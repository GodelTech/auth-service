from src.dyna_config import BASE_URL

from .base import ResponseTypeHandlerBase


class DeviceCodeResponseTypeHandler(ResponseTypeHandlerBase):
    async def get_redirect_url(self, user_id: int) -> str:
        scope_data = await self._parse_scope_data(
            self.auth_service.request_model.scope
        )
        user_code = scope_data["user_code"]
        device = await self.auth_service.device_repo.get_device_by_user_code(
            user_code=user_code
        )
        secret_code = device.device_code.value
        await self.auth_service.persistent_grant_repo.create(
            client_id=self.auth_service.request_model.client_id,
            grant_data=secret_code,
            user_id=user_id,
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
        )
        await self.auth_service.device_repo.delete_by_user_code(
            user_code=user_code
        )
        # TODO if it's not hardcoded url Base class needs to be redefined, because this class
        # TODO is not using _update_redirect_url method
        return f"http://{BASE_URL}/device/auth/success"

    async def _parse_scope_data(self, scope: str) -> dict[str, str]:
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in scope.split("&")
            if len(item.split("=")) == 2
        }
