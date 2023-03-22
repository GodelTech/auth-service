import logging
import random
from string import ascii_uppercase
import secrets
from typing import Any, Optional, Union

from src.dyna_config import DOMAIN_NAME
from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
)
from src.presentation.api.models import DeviceRequestModel, DeviceUserCodeModel, DeviceCancelModel


logger = logging.getLogger('is_app')


class DeviceService:
    def __init__(
            self,
            client_repo: ClientRepository,
            device_repo: DeviceRepository,
    ) -> None:
        self._request_model: Union[DeviceRequestModel, DeviceUserCodeModel, DeviceCancelModel, None] = None
        self.client_repo = client_repo
        self.device_repo = device_repo

    async def get_response(self) -> Optional[dict[str, Any]]:
        if type(self.request_model) == DeviceRequestModel:
            device_code = secrets.token_urlsafe(32)
            user_code = "".join(random.sample(ascii_uppercase, k=8))
            verification_uri = f"http://{DOMAIN_NAME}/device/auth"
            verification_uri_complete = f"http://{DOMAIN_NAME}/device/outh?user_code={user_code}"
            if await self._validate_client(client_id=self.request_model.client_id):
                device_data:dict[str, Any] = {
                    "device_code": device_code,
                    "user_code": user_code,
                    "verification_uri": verification_uri,
                    "verification_uri_complete": verification_uri_complete,
                    "expires_in": 600,
                    "interval": 5
                }
                await self.device_repo.create(client_id=self.request_model.client_id, **device_data)

                return device_data
        return None
    
    async def get_redirect_uri(self) -> str:
        if type(self.request_model) == DeviceUserCodeModel:
            uri_start = f"http://{DOMAIN_NAME}/authorize/?"
            redirect_uri = "https://www.google.com/"
            if self.request_model.user_code is None:
                raise ValueError
            device = await self.device_repo.get_device_by_user_code(user_code=self.request_model.user_code)
            final_uri = uri_start + f"client_id={device.client.client_id}" \
                                    f"&response_type=urn:ietf:params:oauth:grant-type:device_code" \
                                    f"&redirect_uri={redirect_uri}&scope=user_code={self.request_model.user_code}"

            return final_uri
        else:
            raise ValueError

    async def clean_device_data(self) -> str:
        if type(self.request_model) != DeviceCancelModel:
                raise ValueError
        if await self._validate_client(client_id=self.request_model.client_id):
            scope_data={}
            if self.request_model.scope is None:
                scope_data = {'scope':'no_scope'}
            else:
                scope_data = await self._parse_scope_data(scope=self.request_model.scope)
            user_code = scope_data["user_code"]
            if await self._validate_user_code(user_code=user_code):
                await self.device_repo.delete_by_user_code(user_code=user_code)
        return f"http://{DOMAIN_NAME}/device/auth/cancel"

    async def _parse_scope_data(self, scope: str) -> dict[str, str]:
        """ """
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in scope.split("&") if len(item.split("=")) == 2
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
    def request_model(self) -> Union[DeviceRequestModel, DeviceUserCodeModel, DeviceCancelModel, None]:
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: Union[DeviceRequestModel, DeviceUserCodeModel, DeviceCancelModel, None]) -> None:
        self._request_model = request_model