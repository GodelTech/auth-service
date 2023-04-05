from __future__ import annotations
from typing import TYPE_CHECKING
from src.dyna_config import BASE_URL
from src.business_logic.authorization.mixins import CreateGrantMixin

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.data_access.postgresql.repositories import (
        PersistentGrantRepository,
        DeviceRepository,
        UserRepository,
    )


class DeviceAuthService(CreateGrantMixin):
    def __init__(
        self,
        client_validator: ValidatorProtocol,
        redirect_uri_validator: ValidatorProtocol,
        scope_validator: ValidatorProtocol,
        user_credentials_validator: ValidatorProtocol,
        persistent_grant_repo: PersistentGrantRepository,
        user_repo: UserRepository,
        device_repo: DeviceRepository,  # * temporary for tests
    ) -> None:
        self._client_validator = client_validator
        self._redirect_uri_validator = redirect_uri_validator
        self._scope_validator = scope_validator
        self._user_credentials_validator = user_credentials_validator
        self._persistent_grant_repo = persistent_grant_repo
        self._user_repo = user_repo
        self._device_repo = device_repo  # * temporary for tests

    async def _validate_request_data(self, request_data: AuthRequestModel):
        await self._client_validator(request_data.client_id)
        await self._redirect_uri_validator(
            request_data.redirect_uri, request_data.client_id
        )
        await self._scope_validator(request_data.scope, request_data.client_id)
        await self._user_credentials_validator(
            request_data.username, request_data.password
        )
        # * add user_code validation

    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        await self._validate_request_data(request_data)
        scope_data = await self._parse_scope_data(request_data.scope)
        user_code = scope_data["user_code"]
        device = await self._device_repo.get_device_by_user_code(
            user_code=user_code
        )
        grant_data = device.device_code
        await self._create_grant(
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            grant_data=grant_data,
            request_data=request_data,
        )

        await self._device_repo.delete_by_user_code(user_code=user_code)
        return f"http://{BASE_URL}/device/auth/success"
