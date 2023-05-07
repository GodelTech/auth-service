import logging
from typing import Any, Callable

from fastapi import status
from fastapi.responses import JSONResponse
from jwt.exceptions import PyJWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from typing import Any, Callable
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories import BlacklistedTokenRepository
from starlette.responses import RedirectResponse

from src.dyna_config import IS_DEVELOPMENT


logger = logging.getLogger(__name__)

REQUESTS_WITH_AUTH = [
    {"method": "GET", "path": "/userinfo/"},
    {"method": "GET", "path": "/userinfo/jwt"},
    {"method": "POST", "path": "/userinfo/"},
    {"method": "POST", "path": "/introspection/"},
    {"method": "POST", "path": "/revoke/"},
]


class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        blacklisted_repo: BlacklistedTokenRepository,
        jwt_service: JWTService = JWTService(),
    ) -> None:
        self.app = app
        self.jwt_service = jwt_service
        self.blacklisted_repo = blacklisted_repo

    async def dispatch_func(
        self, request: Any, call_next: Callable[..., Any]
    ) -> Any:
        for request_with_auth in REQUESTS_WITH_AUTH:
            if (
                request_with_auth["path"] == request.url.path
                and request_with_auth["method"] == request.method
            ):
                token = request.headers.get(
                    "authorization"
                ) or request.headers.get("auth-swagger")

                if token is None:
                    logger.exception("Authorization Failed")
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content="Incorrect Authorization Token",
                    )
                if await self.blacklisted_repo.exists(
                    token=token,
                ):
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content="Token blacklisted",
                    )
                try:
                    aud = request_with_auth["path"].split("/")[1]
                    if not bool(
                        await self.jwt_service.decode_token(
                            token=token, audience=aud
                        )
                    ):
                        logger.exception("Authorization Failed")
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content="Incorrect Authorization Token",
                        )
                    else:
                        logger.info("Authorization Passed")
                        response = await call_next(request)
                        return response
                except PyJWTError:
                    logger.exception("Authorization Failed")
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content="Incorrect Authorization Token",
                    )
        else:
            logger.info("No Authorization")
            response = await call_next(request)
            # if IS_DEVELOPMENT:
            #     return RedirectResponse(request.url.replace(scheme="https"))
            return response
