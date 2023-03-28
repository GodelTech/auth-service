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
        ResponseTypeHandler,
    )


class ResponseTypeHandlerFactory:
    _handlers: dict[str, Type[ResponseTypeHandler]] = {}

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


# To add new response_type create new class which inherits from ResponseTypeHandler
# and register it like below
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
