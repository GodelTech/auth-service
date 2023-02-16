import logging
import random
import secrets
from string import ascii_uppercase
from typing import Any, Dict, Optional, Union

from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
)
from src.presentation.api.models import (
    DeviceCancelModel,
    DeviceRequestModel,
    DeviceUserCodeModel,
)

logger = logging.getLogger("is_app")


class DeviceService:
    def __init__(
        self,
        client_repo: ClientRepository,
        device_repo: DeviceRepository,
    ) -> None:
        self._request_model: Optional[DeviceRequestModel] = None
        self._request_user_code_model: Optional[DeviceUserCodeModel] = None
        self._request_cancel_model: Optional[DeviceCancelModel] = None
        self.client_repo = client_repo
        self.device_repo = device_repo

    async def get_response(self) -> Optional[Dict[str, Any]]:
        device_code = secrets.token_urlsafe(32)
        user_code = "".join(random.sample(ascii_uppercase, k=8))
        verification_uri = "http://127.0.0.1:8000/device/auth"
        verification_uri_complete = (
            f"http://127.0.0.1:8000/device/outh?user_code={user_code}"
        )
        if self.request_model is not None:
            if await self._validate_client(
                client_id=self.request_model.client_id
            ):
                device_data = {
                    "device_code": device_code,
                    "user_code": user_code,
                    "verification_uri": verification_uri,
                    "verification_uri_complete": verification_uri_complete,
                    "expires_in": 600,
                    "interval": 5,
                }
                await self.device_repo.create(
                    client_id=self.request_model.client_id,
                    device_code=device_code,
                    user_code=user_code,
                    verification_uri=verification_uri,
                    verification_uri_complete=verification_uri_complete,
                    expires_in=600,
                    interval=5,
                )
                return device_data
        return None

    async def get_redirect_uri(self) -> Optional[str]:
        uri_start = "http://127.0.0.1:8000/authorize/?"
        redirect_uri = "https://www.google.com/"
        if self.request_user_code_model is not None:
            device = await self.device_repo.get_device_by_user_code(
                user_code=self.request_user_code_model.user_code
            )
            if device is not None:
                final_uri = (
                    uri_start + f"client_id={device.client_id}"
                    f"&response_type=urn:ietf:params:oauth:grant-type:device_code"
                    f"&redirect_uri={redirect_uri}&scope=user_code={self.request_user_code_model.user_code}"
                )

                return final_uri
        return None

    async def clean_device_data(self) -> Optional[str]:
        if self.request_cancel_model is not None:
            if await self._validate_client(
                client_id=self.request_cancel_model.client_id
            ):
                scope_data = await self._parse_scope_data(
                    scope=self.request_cancel_model.scope
                )
                user_code = scope_data["user_code"]
                if await self._validate_user_code(user_code=user_code):
                    await self.device_repo.delete_by_user_code(
                        user_code=user_code
                    )
            return "http://127.0.0.1:8000/device/auth/cancel"
        return None

    async def _parse_scope_data(self, scope: str) -> Dict[str, Any]:
        """ """
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in scope.split("&")
            if len(item.split("=")) == 2
        }

    async def _validate_user_code(self, user_code: str) -> bool:
        exist = await self.device_repo.validate_user_code(user_code=user_code)
        return exist

    async def _validate_client(self, client_id: str) -> bool:
        """
        Checks if the client is in the database.
        """
        client = await self.client_repo.validate_client_by_client_id(
            client_id=client_id
        )
        return client

    @property
    def request_model(
        self,
    ) -> Optional[DeviceRequestModel]:
        return self._request_model

    @request_model.setter
    def request_model(
        self,
        request_model: Optional[DeviceRequestModel],
    ) -> None:
        self._request_model = request_model

    @property
    def request_user_code_model(
        self,
    ) -> Optional[DeviceUserCodeModel]:
        return self._request_user_code_model

    @request_user_code_model.setter
    def request_user_code_model(
        self,
        request_user_code_model: Optional[DeviceUserCodeModel],
    ) -> None:
        self._request_user_code_model = request_user_code_model

    @property
    def request_cancel_model(
        self,
    ) -> Optional[DeviceCancelModel]:
        return self._request_cancel_model

    @request_cancel_model.setter
    def request_cancel_model(
        self,
        request_cancel_model: Optional[DeviceCancelModel],
    ) -> None:
        self._request_cancel_model = request_cancel_model
