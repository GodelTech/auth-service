from __future__ import annotations

import time
from typing import TYPE_CHECKING

from src.dyna_config import BASE_URL

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.data_access.postgresql.repositories import (
        DeviceRepository,
        PersistentGrantRepository,
        UserRepository,
    )


class DeviceAuthService:
    def __init__(
        self,
        client_validator: ValidatorProtocol,
        redirect_uri_validator: ValidatorProtocol,
        scope_validator: ValidatorProtocol,
        user_credentials_validator: ValidatorProtocol,
        user_code_validator: ValidatorProtocol,
        persistent_grant_repo: PersistentGrantRepository,
        user_repo: UserRepository,
        device_repo: DeviceRepository,
    ) -> None:
        self._client_validator = client_validator
        self._redirect_uri_validator = redirect_uri_validator
        self._scope_validator = scope_validator
        self._user_credentials_validator = user_credentials_validator
        self._user_code_validator = user_code_validator
        self._persistent_grant_repo = persistent_grant_repo
        self._user_repo = user_repo
        self._device_repo = device_repo

    async def _validate_request_data(self, request_data: AuthRequestModel):
        await self._client_validator(request_data.client_id)
        await self._redirect_uri_validator(
            request_data.redirect_uri, request_data.client_id
        )
        await self._scope_validator(request_data.scope, request_data.client_id)
        await self._user_credentials_validator(
            request_data.username, request_data.password
        )
        await self._user_code_validator(request_data.user_code)

    async def _create_grant(
        self, request_data: AuthRequestModel, grant_duration: int
    ):
        await self._persistent_grant_repo.create(
            client_id=request_data.client_id,
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            grant_data=await self._device_repo.get_device_code_by_user_code(
                user_code=request_data.user_code
            ),
            user_id=(await self._user_repo.get_user_by_username(
                request_data.username
            )).id,
            expiration_time=int(time.time()) + grant_duration,
            scope=request_data.scope
        )

    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        await self._validate_request_data(request_data)
        await self._create_grant(request_data=request_data, grant_duration=600)
        await self._device_repo.delete_by_user_code(
            user_code=request_data.user_code
        )
        return f"http://{BASE_URL}/device/auth/success"
