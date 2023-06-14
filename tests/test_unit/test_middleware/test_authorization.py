import json

import mock
import pytest
from fastapi import status
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from src.business_logic.services.jwt_token import JWTService
from src.presentation.api import router
from typing import Any, Callable, MutableMapping
from fastapi import Request
from src.presentation.middleware.authorization_validation import authorization_middleware
from src.data_access.postgresql.repositories import BlacklistedTokenRepository
from sqlalchemy.ext.asyncio import AsyncSession

async def new_decode_token(*args:Any, **kwargs:Any) -> bool:
    return "Bearer AuthToken" in args or "Bearer AuthToken" in kwargs.values()

async def new_call_next(*args:Any, **kwargs:Any) -> str:
    return "Successful"


class NewUrl:
    def __init__(self) -> None:
        self.path = ""


class RequestTest():    
    def __init__(self, session, with_state = True) -> None:
        self.url = NewUrl()
        self.method = ""
        self.headers:dict[str, Any] = {
            "authorization" : None, 
            'auth-swagger' : None
        }
        if with_state:
            self.state = RequestTest(session, with_state=False)
        self.session = session

@pytest.mark.asyncio
class TestAuthorizationMiddleware:
    REQUESTS_WITH_AUTH = [
    {"method": "GET", "path": "/userinfo/"},
    {"method": "GET", "path": "/userinfo/jwt"},
    {"method": "POST", "path": "/userinfo/"},
    {"method": "POST", "path": "/introspection/"},
    {"method": "POST", "path": "/revoke/"},
    ]


    async def test_successful_auth(self, connection: AsyncSession) -> None:

        test_token = "Bearer AuthToken"
        request = RequestTest(connection)

        with mock.patch.object(
            JWTService, "decode_token", new=new_decode_token
        ):
            for request_with_auth in self.REQUESTS_WITH_AUTH:
                request = RequestTest(connection)
                request.method = request_with_auth["method"]
                request.url.path = request_with_auth["path"]
                request.headers["authorization"] = test_token
                await authorization_middleware(request=request, session=connection)

    
    async def test_successful_auth_with_swagger(self, connection: AsyncSession) -> None:
        test_token = "Bearer AuthToken"
        request = RequestTest(connection)

        with mock.patch.object(
            JWTService, "decode_token", new=new_decode_token
        ):
            for request_with_auth in self.REQUESTS_WITH_AUTH:
                request = RequestTest(connection)
                request.method = request_with_auth["method"]
                request.url.path = request_with_auth["path"]
                request.headers["auth-swagger"] = test_token

                middleware = await authorization_middleware(request=request, session=connection)

    # async def test_without_token(self,connection: AsyncSession) -> None:
    #     request = RequestTest(connection)
    #     request.method = REQUESTS_WITH_AUTH[0]["method"]
    #     request.url.path = REQUESTS_WITH_AUTH[0]["path"]
    #     middleware = AuthorizationMiddleware(app=ASGIApp)
    #     response = await middleware.dispatch_func(
    #         request=request, call_next=new_call_next
    #     )
    #     response_content = json.loads(response.body.decode("utf-8"))
    #     assert response_content == "Incorrect Authorization Token"
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # async def test_incorrect_token(self, connection: AsyncSession) -> None:
    #     with mock.patch.object(
    #         JWTService, "decode_token", new=new_decode_token
    #     ):
    #         request = RequestTest(connection)
    #         request.method = REQUESTS_WITH_AUTH[0]["method"]
    #         request.url.path = REQUESTS_WITH_AUTH[0]["path"]
    #         request.headers["authorization"] = "Bearer FALSE_AuthToken"
    #         middleware = AuthorizationMiddleware(app=ASGIApp)
    #         response = await middleware.dispatch_func(
    #             request=request, call_next=new_call_next
    #         )
    #         response_content = json.loads(response.body.decode("utf-8"))
    #         assert response_content == "Incorrect Authorization Token"
    #         assert response.status_code == status.HTTP_401_UNAUTHORIZED


    # async def test_token_with_incorrect_signature(self, connection: AsyncSession) -> None:
    #     request = RequestTest(connection)
    #     request.method = REQUESTS_WITH_AUTH[0]["method"]
    #     request.url.path = REQUESTS_WITH_AUTH[0]["path"]
    #     request.headers["authorization"] = "incorrect-token"
    #     middleware = AuthorizationMiddleware(app=ASGIApp)
    #     response = await middleware.dispatch_func(
    #         request=request, call_next=new_call_next
    #     )
    #     response_content = json.loads(response.body.decode("utf-8"))
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED
    #     assert response_content == "Incorrect Authorization Token"