import logging
from typing import Any, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any, Callable

from src.dyna_config import IS_DEVELOPMENT


logger = logging.getLogger(__name__)

class HttpsGlobalMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any) -> None:
        self.app = app

    async def dispatch_func(self, request, call_next:Callable[..., Any]) -> Any:
            if IS_DEVELOPMENT:
                if request.scope["scheme"] != "https":
                    logger.debug(f'Scheme change: {request.scope["scheme"]} --> https')
                    request.scope["scheme"] = "https"
            response = await call_next(request)
            return response