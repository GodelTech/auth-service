from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from client_example.utils import client


class UserIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        token = request.headers.get("authorization") or request.cookies.get(
            "access_token"
        )
        if token is not None:
            user_id = await client.get_id(token)
            request.state.user_id = user_id

        response = await call_next(request)
        return response
