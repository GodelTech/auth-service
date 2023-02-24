import logging
import secrets
from typing import Any, Dict, Optional

from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.tokens import get_single_token
from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
    PersistentGrantRepository,
    UserRepository,
)
from src.presentation.api.models import RequestModel

logger = logging.getLogger(__name__)


class AuthorizationService:
    def __init__(
        self,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        device_repo: DeviceRepository,
        password_service: PasswordHash,
        jwt_service: JWTService,
    ) -> None:
        self._request_model: Optional[RequestModel] = None
        self.client_repo = client_repo
        self.user_repo = user_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.device_repo = device_repo
        self.password_service = password_service
        self.jwt_service = jwt_service

    async def save_code_challenge_data(self) -> dict:
        code_challenge = self.request_model.code_challenge
        if code_challenge:
            scope_data = await self._parse_scope_data(
                )
                    scope=self.request_model.scope
            user_name = scope_data["username"]
            
            (
                user_hash_password,
                user_id,
            ) = await self.user_repo.get_hash_password(user_name)

            await self.persistent_grant_repo.create(
                grant_data=code_challenge,
                client_id=self.request_model.client_id,
                user_id=user_id,
                grant_type="code_challenge")

    async def get_redirect_url(self) -> Optional[str]:
        if (
            self.request_model is not None
            and self.request_model.scope is not None
        ):
            if await self._validate_client(self.request_model.client_id):
                scope_data = await self._parse_scope_data(
                    scope=self.request_model.scope
                )
                password = scope_data["password"]
                user_name = scope_data["username"]

                (
                    user_hash_password,
                    user_id,
                ) = await self.user_repo.get_hash_password(user_name)
                validated = self.password_service.validate_password(
                    password, user_hash_password
                )

                if user_hash_password and validated:
                    if self.request_model.response_type == "code":
                        return await self.get_redirect_url_code_response_type(
                            user_id=user_id
                        )
                    elif self.request_model.response_type == "token":
                        return await self.get_redirect_url_token_response_type(
                            user_id=user_id
                        )
                    elif self.request_model.response_type == "id_token token":
                        return await self.get_redirect_url_id_token_token_response_type(
                            user_id=user_id
                        )
                    elif (
                        self.request_model.response_type
                        == "urn:ietf:params:oauth:grant-type:device_code"
                    ):
                        return await self.get_redirect_url_device_code_response_type(
                            user_id=user_id
                        )
        return None

    async def get_redirect_url_code_response_type(
        self, user_id: int
    ) -> Optional[str]:
        secret_code = secrets.token_urlsafe(32)
        if self.request_model is not None:
            await self.persistent_grant_repo.create(
                client_id=self.request_model.client_id,
                grant_data=secret_code,
                user_id=user_id,
            )

            return await self._update_redirect_url_with_params(
                secret_code=secret_code
            )
        return None

    async def get_redirect_url_device_code_response_type(
        self, user_id: int
    ) -> Optional[str]:
        if (
            self.request_model is not None
            and self.request_model.scope is not None
        ):
            scope_data = await self._parse_scope_data(
                scope=self.request_model.scope
            )
            user_code = scope_data["user_code"]
            device = await self.device_repo.get_device_by_user_code(
                user_code=user_code
            )
            secret_code = device.device_code
            await self.persistent_grant_repo.create(
                client_id=self.request_model.client_id,
                grant_data=secret_code,
                user_id=user_id,
                grant_type="urn:ietf:params:oauth:grant-type:device_code",
            )
            await self.device_repo.delete_by_user_code(user_code=user_code)

            return "http://127.0.0.1:8000/device/auth/success"
        return None

    async def get_redirect_url_token_response_type(
        self, user_id: int
    ) -> Optional[str]:
        expiration_time = 600
        if self.request_model is not None:
            scope = {"scopes": self.request_model.scope}
            access_token = await get_single_token(
                user_id=user_id,
                client_id=self.request_model.client_id,
                additional_data=scope,
                jwt_service=self.jwt_service,
                expiration_time=expiration_time,
            )

            uri_data = (
                f"access_token={access_token}&expires_in={expiration_time}&state={self.request_model.state}"
                f"&token_type=Bearer"
            )
            result_uri = self.request_model.redirect_uri + "?" + uri_data
            return result_uri
        return None

    async def get_redirect_url_id_token_token_response_type(
        self, user_id: int
    ) -> Optional[str]:
        expiration_time = 600
        if self.request_model is not None:
            scope = {"scopes": self.request_model.scope}
            claims = await self.user_repo.get_claims(
                id=1
            )  # change to user_id when database will be ready
            access_token = await get_single_token(
                user_id=user_id,
                client_id=self.request_model.client_id,
                additional_data=scope,
                jwt_service=self.jwt_service,
                expiration_time=expiration_time,
            )
            id_token = await get_single_token(
                user_id=user_id,
                client_id=self.request_model.client_id,
                additional_data=claims,
                jwt_service=self.jwt_service,
                expiration_time=expiration_time,
            )

            uri_data = (
                f"access_token={access_token}&expires_in={expiration_time}&state={self.request_model.state}"
                f"&id_token={id_token}&token_type=Bearer"
            )
            result_uri = self.request_model.redirect_uri + "?" + uri_data
            return result_uri
        return None

    async def _validate_client(self, client_id: str) -> bool:
        """
        Checks if the client is in the database.
        """
        client = await self.client_repo.get_client_by_client_id(
            client_id=client_id
        )
        return client

    async def _parse_scope_data(self, scope: str) -> Dict[str, Any]:
        """ """
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in scope.split("&")
            if len(item.split("=")) == 2
        }

    async def _update_redirect_url_with_params(
        self, secret_code: str
    ) -> Optional[str]:
        if self.request_model is not None:
            redirect_uri = (
                f"{self.request_model.redirect_uri}?code={secret_code}"
            )
            if self.request_model.state:
                redirect_uri += f"&state={self.request_model.state}"

            return redirect_uri
        return None

    @property
    def request_model(self) -> Optional[RequestModel]:
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: RequestModel) -> None:
        self._request_model = request_model
