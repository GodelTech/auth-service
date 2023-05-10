import logging
from typing import Any, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.di.providers import provide_async_session_stub
from typing import Callable, Any
from src.presentation.admin_api.models.group import *
logger = logging.getLogger(__name__)

REQUESTS_WITHOUT_SESSION = [
    # {"method": "GET", "path": "/userinfo/"},
    # {"method": "GET", "path": "/userinfo/jwt"},
    # {"method": "POST", "path": "/userinfo/"},
    # {"method": "POST", "path": "/introspection/"},
    # {"method": "POST", "path": "/revoke/"},
]


class SessionManager(BaseHTTPMiddleware):
    def __init__(self, app: Any, session:AsyncSession) -> None:
        self.app = app
        self.session_gnerator = session
   
    async def dispatch_func(self, request: Any, call_next:Callable[..., Any]) -> Any:
        if True:
            async for session in self.session_gnerator():
                session:AsyncSession
                try:
                    request.state.session = session
                    response = await call_next(request)
                except:
                    await session.rollback()
                    raise
                else:
                    # if len(session.dirty)+len(session.deleted)+len(session.new)!=0:
                    await session.commit()
                    return response
                finally:
                    await session.close()
                    # break

        else:
            response = await call_next(request)
            return response
