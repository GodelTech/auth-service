from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

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
                token = request.headers.get('authorization')
                if token is None:
                    token = request.headers.get('auth-swagger')

                if token is None:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content="Incorrect Authorization Token",
                    )

                # TODO modify it to catch expired signature
                try:
                    if not bool(
                        await self.token_validator.is_token_valid(token)
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
                        content="Incorrect Authorization Token",
                    )
        else:
            response = await call_next(request)
            return response
