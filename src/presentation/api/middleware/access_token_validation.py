import logging

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from typing import Callable, Any, Union
from src.business_logic.services import JWTService
from src.data_access.postgresql.repositories import BlacklistedTokenRepository
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def dispatch_func(self, request: Any, call_next:Callable[..., Any]) -> Any:

        if "/administration/" in request.url.path:
            token = request.headers.get("access-token")

            try:
                if token is None:
                    raise ValueError
                if await self.blacklisted_repo.exists(
                        token=token,
                    ):
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content="Token revoked"
                    )
                if not await self.jwt_service.verify_token(token, aud='admin'):
                    logger.exception("403 Incorrect Access Token")
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content="Incorrect Access Token",
                    )
                    
                else:
                    logger.info("Access Token Auth Passed")
                    response = await call_next(request)
                    return response
            except:
                logger.exception("403 Incorrect Access Token")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content="Incorrect Access Token",
                )
        else:
            response = await call_next(request)
            return response
