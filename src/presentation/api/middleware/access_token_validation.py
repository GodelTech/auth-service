import logging
from pydantic import ValidationError
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from typing import Callable, Any, Union
from src.business_logic.services import JWTService
from src.data_access.postgresql.repositories import BlacklistedTokenRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.errors import IncorrectAuthTokenError

logger = logging.getLogger(__name__)


class AccessTokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, 
                 app: Any, 
                 blacklisted_repo: BlacklistedTokenRepository,
                 jwt_service: JWTService = JWTService(), 
                 ):
        self.app = app
        self.jwt_service = jwt_service
        self.blacklisted_repo = blacklisted_repo

    async def dispatch_func(self, request: Request, call_next:Callable[..., Any]) -> Any:

        if "/administration/" in request.url.path or (
            request.url.path == "/clients" and request.method == 'GET'
            ):
            token = request.headers.get("access-token")

            if token is None:
                raise IncorrectAuthTokenError
            if await self.blacklisted_repo.exists(
                    token=token,
                ):
                raise IncorrectAuthTokenError
            
            if not await self.jwt_service.verify_token(token, aud='admin'):
                raise IncorrectAuthTokenError
            
            
        response = await call_next(request)
        return response
