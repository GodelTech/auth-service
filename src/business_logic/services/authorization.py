import logging
import secrets
from typing import Optional, Type
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
from src.data_access.postgresql.errors import WrongResponseTypeError


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

        # TODO this method actually validates both client_id and redirect_uri -> we need to refactor client repo for sure
        # validate client_id and client_redirect_uri
        await self.client_repo.validate_client_redirect_uri(
            self.request_model.client_id, self.request_model.redirect_uri
        )
        # get hashed_password and validate it
        (
            hashed_password,
            user_id,
        ) = await self.user_repo.get_hash_password(self.request_model.username)
        self.password_service.validate_password(
            self.request_model.password, hashed_password
        )

        handler = ResponseTypeHandlerFactory.get_handler(
            self.request_model.response_type, auth_service=self
        )
        return await handler.get_redirect_url(
            user_id, request_model=self.request_model
        )


class ResponseTypeHandler(ABC):
    def __init__(self, auth_service: AuthorizationService) -> None:
        self.auth_service = auth_service

    @abstractmethod
    async def get_redirect_url(
        self, user_id: int, request_model: DataRequestModel
    ) -> str:
        pass

    async def _update_redirect_url_with_params(
        self, secret_code: str, request_model: DataRequestModel
    ) -> str:
        redirect_uri = f"{request_model.redirect_uri}?code={secret_code}"
        if request_model.state:
            redirect_uri += f"&state={request_model.state}"
        return redirect_uri

    async def _parse_scope_data(self, scope: str) -> dict[str, str]:
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in scope.split("&")
            if len(item.split("=")) == 2
        }


class CodeResponseTypeHandler(ResponseTypeHandler):
    async def get_redirect_url(
        self, user_id: int, request_model: DataRequestModel
    ) -> str:
        secret_code = secrets.token_urlsafe(32)
        await self.auth_service.persistent_grant_repo.create(
            client_id=request_model.client_id,
            grant_data=secret_code,
            user_id=user_id,
        )
        return await self._update_redirect_url_with_params(
            secret_code, request_model
        )


class TokenResponseTypeHandler(ResponseTypeHandler):
    async def get_redirect_url(
        self, user_id: int, request_model: DataRequestModel
    ) -> str:
        expiration_time = 600
        scope = {"scopes": request_model.scope}
        access_token = await get_single_token(
            user_id=user_id,
            client_id=request_model.client_id,
            additional_data=scope,
            jwt_service=self.jwt_service,
            expiration_time=expiration_time,
        )

        uri_data = (
            f"access_token={access_token}&expires_in={expiration_time}&state={request_model.state}"
            f"&token_type=Bearer"
        )
        result_uri = request_model.redirect_uri + "?" + uri_data
        return result_uri


class IdTokenTokenResponseTypeHandler(ResponseTypeHandler):
    async def get_redirect_url(
        self, user_id: int, request_model: DataRequestModel
    ) -> str:
        expiration_time = 600
        scope = {"scopes": request_model.scope}
        claims = await self.user_repo.get_claims(
            id=1
        )  # change to user_id when database will be ready
        access_token = await get_single_token(
            user_id=user_id,
            client_id=request_model.client_id,
            additional_data=scope,
            jwt_service=self.jwt_service,
            expiration_time=expiration_time,
            aud=["userinfo", "introspection", "revoke"],
        )
        id_token = await get_single_token(
            user_id=user_id,
            client_id=request_model.client_id,
            additional_data=claims,
            jwt_service=self.jwt_service,
            expiration_time=expiration_time,
        )

        uri_data = (
            f"access_token={access_token}&expires_in={expiration_time}&state={request_model.state}"
            f"&id_token={id_token}&token_type=Bearer"
        )
        result_uri = request_model.redirect_uri + "?" + uri_data
        return result_uri


class DeviceCodeResponseTypeHandler(ResponseTypeHandler):
    async def get_redirect_url(
        self, user_id: int, request_model: DataRequestModel
    ) -> str:
        scope_data = await self._parse_scope_data(scope=request_model.scope)
        user_code = scope_data["user_code"]
        device = await self.device_repo.get_device_by_user_code(
            user_code=user_code
        )
        secret_code = device.device_code.value
        await self.persistent_grant_repo.create(
            client_id=request_model.client_id,
            grant_data=secret_code,
            user_id=user_id,
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
        )
        await self.device_repo.delete_by_user_code(user_code=user_code)
        return f"http://{BASE_URL}/device/auth/success"


class ResponseTypeHandlerFactory:
    _handlers = {}

    @staticmethod
    def register_handler(
        response_type: str, handler: Type[ResponseTypeHandler]
    ) -> None:
        ResponseTypeHandlerFactory._handlers[response_type] = handler

    @staticmethod
    def get_handler(
        response_type: str, auth_service: AuthorizationService
    ) -> ResponseTypeHandler:
        handler = ResponseTypeHandlerFactory._handlers.get(response_type)
        if not handler:
            raise WrongResponseTypeError
        return handler(auth_service)


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
