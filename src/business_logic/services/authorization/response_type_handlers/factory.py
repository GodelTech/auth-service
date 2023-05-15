from __future__ import annotations

from typing import TYPE_CHECKING, Type

from src.business_logic.services.authorization.response_type_handlers import (
    CodeResponseTypeHandler,
    DeviceCodeResponseTypeHandler,
    IdTokenResponseTypeHandler,
    IdTokenTokenResponseTypeHandler,
    TokenResponseTypeHandler,
)
from src.data_access.postgresql.errors import WrongResponseTypeError

if TYPE_CHECKING:
    from src.business_logic.services.authorization.authorization_service import (
        AuthorizationService,
    )
    from src.business_logic.services.authorization.response_type_handlers import (
        ResponseTypeHandlerProtocol,
    )


class ResponseTypeHandlerFactory:
    _handlers: dict[str, Type[ResponseTypeHandlerProtocol]] = {}

    @classmethod
    def register_handler(
        cls, response_type: str, handler: Type[ResponseTypeHandlerProtocol]
    ) -> None:
        cls._handlers[response_type] = handler

    @classmethod
    def get_handler(
        cls, auth_service: AuthorizationService
    ) -> ResponseTypeHandlerProtocol:
        handler = cls._handlers.get(auth_service.request_model.response_type)
        if not handler:
            raise WrongResponseTypeError("Provided response_type is invalid.")
        return handler(auth_service)


ResponseTypeHandlerFactory.register_handler("code", CodeResponseTypeHandler)
ResponseTypeHandlerFactory.register_handler("token", TokenResponseTypeHandler)
ResponseTypeHandlerFactory.register_handler(
    "id_token", IdTokenResponseTypeHandler
)
ResponseTypeHandlerFactory.register_handler(
    "id_token token", IdTokenTokenResponseTypeHandler
)
ResponseTypeHandlerFactory.register_handler(
    "urn:ietf:params:oauth:grant-type:device_code",
    DeviceCodeResponseTypeHandler,
)
