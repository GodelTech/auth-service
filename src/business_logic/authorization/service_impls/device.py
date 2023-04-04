from __future__ import annotations
from typing import TYPE_CHECKING
from src.dyna_config import BASE_URL

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.data_access.postgresql.repositories import (
        PersistentGrantRepository,
        DeviceRepository,
        UserRepository,
    )


class DeviceAuthService:
    def __init__(
        self,
        client_validator: ValidatorProtocol,
        redirect_uri_validator: ValidatorProtocol,
        scope_validator: ValidatorProtocol,
        user_credentials_validator: ValidatorProtocol,
        # * temporary for tests
        persistent_grant_repo: PersistentGrantRepository,
        device_repo: DeviceRepository,
        user_repo: UserRepository,
    ) -> None:
        self._client_validator = client_validator
        self._redirect_uri_validator = redirect_uri_validator
        self._scope_validator = scope_validator
        self._user_credentials_validator = user_credentials_validator
        # * temporary for tests
        self._persistent_grant_repo = persistent_grant_repo
        self._device_repo = device_repo
        self._user_repo = user_repo

    async def _parse_scope_data(self, scope: str) -> dict[str, str]:
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in scope.split("&")
            if len(item.split("=")) == 2
        }

    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        scope_data = await self._parse_scope_data(request_data.scope)
        user_code = scope_data["user_code"]
        device = await self._device_repo.get_device_by_user_code(
            user_code=user_code
        )
        user_id = await self._user_repo.get_user_id_by_username(
            request_data.username
        )
        secret_code = device.device_code
        await self._persistent_grant_repo.create(
            client_id=request_data.client_id,
            grant_data=secret_code,
            user_id=user_id,
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
        )
        await self._device_repo.delete_by_user_code(user_code=user_code)
        return f"http://{BASE_URL}/device/auth/success"
