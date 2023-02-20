from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from client_example.utils import client


class UserIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        self.app = app
        self.endpoint = "/notes"

    async def dispatch_func(self, request: Request, call_next) -> Response:
        if self.endpoint in request.url.path:
            # TODO how to avoid using request.cookies?
            token = request.headers.get(
                "authorization"
            ) or request.cookies.get("access_token")
            if token is not None:
                user_id = await client.get_id(token)
                request.state.user_id = user_id

        response = await call_next(request)
        return response
