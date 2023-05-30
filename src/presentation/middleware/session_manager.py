import logging
from typing import Any, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Any
logger = logging.getLogger(__name__)


class SessionManager(BaseHTTPMiddleware):
    def __init__(self, app: Any, session:AsyncSession) -> None:
        self.app = app
        self.session_gnerator = session
   
    async def dispatch_func(self, request: Any, call_next:Callable[..., Any]) -> Any:
        if not '.well-known/jwks' in request.url.__str__():
            async for session in self.session_gnerator():
                session:AsyncSession
                try:
                    request.state.session = session
                    response = await call_next(request)
                except:
                    await session.rollback()
                    raise
                else:
                    await session.commit()
                    return response
                finally:
                    await session.close()

        else:
            response = await call_next(request)
            return response
