import logging
from json import JSONDecodeError

from fastapi import Request, status
from fastapi.responses import JSONResponse
from jwt import ExpiredSignatureError, PyJWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from client_example.api.routers.auth import client
from client_example.httpx_oauth.oauth2 import RefreshTokenError
from client_example.utils import TokenValidator

logger = logging.getLogger("example_app")


class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: ASGIApp, token_validator: TokenValidator = TokenValidator()
    ):
        self.app = app
        self.token_validator = token_validator
        self.protected_endpoints = ('/notes', '/logout')

    async def dispatch_func(self, request: Request, call_next):
        if any(
            endpoint in request.url.path
            for endpoint in self.protected_endpoints
        ):
            access_token = request.headers.get('authorization')

            try:
                await self.token_validator.is_token_valid(access_token)
                logger.info("Authorization passed")
                response = await call_next(request)
                return response

            except ExpiredSignatureError:
                logger.info("Token has expired. Refreshing the token...")
                return await self.get_new_token(request, call_next)

            # AttributeError handles not providing token at all
            except (PyJWTError, AttributeError) as e:
                logger.exception("Authorization failed", e)
                return self._get_unauthorized_response()

        response = await call_next(request)
        return response

    async def get_new_token(self, request: Request, call_next):
        # ! probably will need to change it in a future - due to token service modifications
        # TODO catch when refresh token is expired and logout the user?
        try:
            refresh_token = await request.json()
            refresh_token = refresh_token.get("refresh_token")

            if refresh_token is not None:
                new_token = await client.refresh_token(refresh_token)
                # if expired return 401
                new_access_token = new_token.get("access_token")
                # save new token on client side
                logger.info("New token created")
                return await self._validate_new_token(
                    new_access_token, request, call_next
                )
            logger.info("Incorrect refresh token")
            return self._get_unauthorized_response()

        except (RefreshTokenError, JSONDecodeError):
            return self._get_unauthorized_response()

    async def _validate_new_token(
        self, new_token: str, request: Request, call_next
    ):
        try:
            await self.token_validator.is_token_valid(new_token)
            logger.info("New token validated")
            response = await call_next(request)
            return response

        except PyJWTError as e:
            logger.exception("Incorrect new access token", e)
            return self._get_unauthorized_response()

    def _get_unauthorized_response(self):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Incorrect Authorization Token",
        )
