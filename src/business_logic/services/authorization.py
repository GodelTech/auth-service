import logging
import secrets
from typing import Any, Dict, Optional, Type
from abc import ABC, abstractmethod

from src.dyna_config import BASE_URL
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.tokens import get_single_token
from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
    PersistentGrantRepository,
    UserRepository,
)
from src.presentation.api.models import DataRequestModel

logger = logging.getLogger(__name__)


class ResponseTypeHandler(ABC):
    @abstractmethod
    async def get_redirect_url(self, user_id: int) -> Optional[str]:
        pass


class CodeResponseTypeHandler(ResponseTypeHandler):
    async def get_redirect_url(self, user_id: int) -> Optional[str]:
        pass


class TokenResponseTypeHandler(ResponseTypeHandler):
    async def get_redirect_url(self, user_id: int) -> Optional[str]:
        pass


class IdTokenTokenResponseTypeHandler(ResponseTypeHandler):
    async def get_redirect_url(self, user_id: int) -> Optional[str]:
        pass


class DeviceCodeResponseTypeHandler(ResponseTypeHandler):
    async def get_redirect_url(self, user_id: int) -> Optional[str]:
        pass


class ResponseTypeHandlerFactory:
    _handlers = {}

    @staticmethod
    def register_handler(
        response_type: str, handler: Type[ResponseTypeHandler]
    ) -> None:
        ResponseTypeHandlerFactory._handlers[response_type] = handler

    @staticmethod
    def get_handler(response_type: str) -> Optional[ResponseTypeHandler]:
        handler = ResponseTypeHandlerFactory._handlers.get(response_type)
        return (
            handler() if handler else None
        )  # TODO instead of None raise Exception -> unsupported_response_type


# Register the response type handlers with the factory
ResponseTypeHandlerFactory.register_handler("code", CodeResponseTypeHandler)
ResponseTypeHandlerFactory.register_handler("token", TokenResponseTypeHandler)
ResponseTypeHandlerFactory.register_handler(
    "id_token token", IdTokenTokenResponseTypeHandler
)
ResponseTypeHandlerFactory.register_handler(
    "urn:ietf:params:oauth:grant-type:device_code",
    DeviceCodeResponseTypeHandler,
)


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
        self._request_model: Optional[DataRequestModel] = None
        self.client_repo = client_repo
        self.user_repo = user_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.device_repo = device_repo
        self.password_service = password_service
        self.jwt_service = jwt_service

    @property
    def request_model(self) -> Optional[DataRequestModel]:
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: DataRequestModel) -> None:
        self._request_model = request_model

    async def get_redirect_url(self) -> Optional[str]:
        if self.request_model is None or self.request_model.scope is None:
            return None

        if await self._validate_client(
            self.request_model.client_id
        ) and await self._validate_client_redirect_uri(
            self.request_model.client_id, self.request_model.redirect_uri
        ):
            (
                hashed_password,
                user_id,
            ) = await self.user_repo.get_hash_password(
                self.request_model.username
            )
            validated = self.password_service.validate_password(
                self.request_model.password, hashed_password
            )

            if hashed_password and validated:
                handler = ResponseTypeHandlerFactory.get_handler(
                    self.request_model.response_type
                )
                if handler:
                    return await handler.get_redirect_url(user_id=user_id)

    async def get_redirect_url_code_response_type(
        self, user_id: int
    ) -> Optional[str]:
        if self.request_model is None:
            return None

        secret_code = secrets.token_urlsafe(32)
        await self.persistent_grant_repo.create(
            client_id=self.request_model.client_id,
            grant_data=secret_code,
            user_id=user_id,
        )
        return await self._update_redirect_url_with_params(
            secret_code=secret_code
        )

    async def get_redirect_url_device_code_response_type(
        self, user_id: int
    ) -> Optional[str]:
        if self.request_model is None or self.request_model.scope is None:
            return None

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
        return f"http://{BASE_URL}/device/auth/success"

    async def get_redirect_url_token_response_type(
        self, user_id: int
    ) -> Optional[str]:
        if self.request_model is None:
            return None

    async def get_redirect_url_id_token_token_response_type(
        self, user_id: int
    ) -> Optional[str]:
        if self.request_model is None:
            return None

        expiration_time = 600
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
            aud=["userinfo", "introspection", "revoke"],
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

    async def _validate_client(self, client_id: str) -> Optional[bool]:
        """
        Checks if the client is in the database.
        """
        if self.request_model is None:
            return None

        client = await self.client_repo.get_client_by_client_id(
            client_id=client_id
        )
        return client

    async def _validate_client_redirect_uri(  # TODO create mixin
        self, client_id: str, redirect_uri: str
    ) -> bool:
        """
        Checks if the redirect uri is in the database.
        """
        client = await self.client_repo.validate_client_redirect_uri(
            client_id=client_id, redirect_uri=redirect_uri
        )
        return client

    async def _parse_scope_data(self, scope: str) -> dict[str, str]:
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in scope.split("&")
            if len(item.split("=")) == 2
        }

    async def _update_redirect_url_with_params(
        self, secret_code: str
    ) -> Optional[str]:
        if self.request_model is None:
            return None

        redirect_uri = f"{self.request_model.redirect_uri}?code={secret_code}"
        if self.request_model.state:
            redirect_uri += f"&state={self.request_model.state}"
        return redirect_uri
