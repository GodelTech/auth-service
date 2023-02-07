from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from client_example.utils import is_token_valid_test

REQUESTS_WITH_AUTH = [
    {"method": "GET", 'path': '/notes/'},
    {"method": "POST", 'path': '/notes/'},
]


class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        self.app = app

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
                    if not bool(await is_token_valid_test(token)):
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
