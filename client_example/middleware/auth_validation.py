import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from client_example.routers.auth import client
from client_example.utils import TokenValidator

REQUESTS_WITH_AUTH = [
    {"method": "GET", 'path': '/notes/'},
    {"method": "POST", 'path': '/notes/'},
]


class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: ASGIApp, token_validator: TokenValidator = TokenValidator()
    ):
        self.app = app
        self.token_validator = token_validator

    async def dispatch_func(self, request: Request, call_next):
        for request_with_auth in REQUESTS_WITH_AUTH:
            if (
                request_with_auth["path"] == request.url.path
                and request_with_auth["method"] == request.method
            ):
                access_token = request.headers.get('authorization')

                if access_token is None:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content="Incorrect Authorization Token",
                    )

                # TODO modify it to catch expired signature
                try:
                    if not bool(
                        await self.token_validator.is_token_valid(access_token)
                    ):
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content="Incorrect Authorization Token",
                        )
                    else:
                        response = await call_next(request)
                        return response
                except jwt.exceptions.ExpiredSignatureError as e:
                    print(e)

                    refresh_token = request.cookies.get('refresh_token')

                    if refresh_token is None:
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content="Incorrect Refresh Token",
                        )

                    # todo there is no error handling in token service
                    new_token = await client.refresh_token(refresh_token)
                    # if expired return 401
                    new_access_token = new_token['access_token']

                    # save new access token to client

                    try:
                        if not bool(
                            await self.token_validator.is_token_valid(
                                new_access_token
                            )
                        ):
                            return JSONResponse(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                content="Incorrect Authorization Token",
                            )
                        else:
                            response = await call_next(request)
                            return response

                    except:
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content="Incorrect Refresh Token",
                        )
        else:
            response = await call_next(request)
            return response
