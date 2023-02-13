import logging
import random
from string import ascii_uppercase
import secrets

from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
)
from src.presentation.api.models import RequestModel


logger = logging.getLogger('is_app')


class DeviceService:
    def __init__(
            self,
            client_repo: ClientRepository,
            device_repo: DeviceRepository,
    ) -> None:
        self._request_model = None
        self.client_repo = client_repo
        self.device_repo = device_repo

    async def get_response(self):
        device_code = secrets.token_urlsafe(32)
        user_code = "".join(random.sample(ascii_uppercase, k=8))
        verification_uri = "http://127.0.0.1:8000/device/auth"
        verification_uri_complete = f"http://127.0.0.1:8000/device/outh?user_code={user_code}"
        if await self._validate_client(client_id=self.request_model.client_id):
            device_data = {
                "device_code": device_code,
                "user_code": user_code,
                "verification_uri": verification_uri,
                "verification_uri_complete": verification_uri_complete,
                "expires_in": 600,
                "interval": 5
            }
            await self.device_repo.create(client_id=self.request_model.client_id, **device_data)

            return device_data

    async def get_redirect_uri(self) -> str:
        uri_start = "http://127.0.0.1:8000/authorize/?"
        redirect_uri = "https://www.google.com/"
        device = await self.device_repo.get_device_by_user_code(user_code=self.request_model.user_code)
        final_uri = uri_start + f"client_id={device.client_id}" \
                                f"&response_type=urn:ietf:params:oauth:grant-type:device_code" \
                                f"&redirect_uri={redirect_uri}&scope=user_code={self.request_model.user_code}"

        return final_uri

    async def clean_device_data(self) -> str:
        if await self._validate_client(client_id=self.request_model.client_id):
            scope_data = await self._parse_scope_data(scope=self.request_model.scope)
            user_code = scope_data["user_code"]
            if await self._validate_user_code(user_code=user_code):
                await self.device_repo.delete_by_user_code(user_code=user_code)
        return "http://127.0.0.1:8000/device/auth/cancel"

    async def _parse_scope_data(self, scope: str) -> dict:
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
    def request_model(self) -> None:
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: RequestModel) -> None:
        self._request_model = request_model
