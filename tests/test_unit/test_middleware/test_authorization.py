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
from src.presentation.api.middleware.authorization_validation import AuthorizationMiddleware, REQUESTS_WITH_AUTH
from src.data_access.postgresql.repositories import BlacklistedTokenRepository

async def new_decode_token(*args:Any, **kwargs:Any) -> bool:
    return "Bearer AuthToken" in args or "Bearer AuthToken" in kwargs.values()

async def new_call_next(*args:Any, **kwargs:Any) -> str:
    return "Successful"


class NewUrl:
    def __init__(self) -> None:
        self.path = ""


class RequestTest():    
    def __init__(self) -> None:
        self.url = NewUrl()
        self.method = ""
        self.headers:dict[str, Any] = {
            "authorization" : None, 
            'auth-swagger' : None
        }


@pytest.mark.asyncio
class TestAuthorizationMiddleware:
    async def test_successful_auth(self, engine: AsyncEngine) -> None:

        test_token = "Bearer AuthToken"
        request = RequestTest()

        with mock.patch.object(
            JWTService, "decode_token", new=new_decode_token
        ):
            for request_with_auth in REQUESTS_WITH_AUTH:
                request = RequestTest()
                request.method = request_with_auth["method"]
                request.url.path = request_with_auth["path"]
                request.headers["authorization"] = test_token
                middleware = AuthorizationMiddleware(app = ASGIApp, blacklisted_repo=BlacklistedTokenRepository(engine))
                assert await middleware.dispatch_func(request=request, call_next=new_call_next) == 'Successful'
    
    async def test_successful_auth_with_swagger(self, engine: AsyncEngine) -> None:
        test_token = "Bearer AuthToken"
        request = RequestTest()

        with mock.patch.object(
            JWTService, "decode_token", new=new_decode_token
        ):
            for request_with_auth in REQUESTS_WITH_AUTH:
                request = RequestTest()
                request.method = request_with_auth["method"]
                request.url.path = request_with_auth["path"]
                request.headers["auth-swagger"] = test_token

                middleware = AuthorizationMiddleware(app=ASGIApp, blacklisted_repo=BlacklistedTokenRepository(engine))
                assert (
                    await middleware.dispatch_func(
                        request=request, call_next=new_call_next
                    )
                    == "Successful"
                )

    async def test_without_token(self, engine: AsyncEngine) -> None:
        request = RequestTest()
        request.method = REQUESTS_WITH_AUTH[0]["method"]
        request.url.path = REQUESTS_WITH_AUTH[0]["path"]
        middleware = AuthorizationMiddleware(app=ASGIApp, blacklisted_repo=BlacklistedTokenRepository(engine))
        response = await middleware.dispatch_func(
            request=request, call_next=new_call_next
        )
        response_content = json.loads(response.body.decode("utf-8"))
        assert response_content == "Incorrect Authorization Token"
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_incorrect_token(self, engine: AsyncEngine) -> None:
        with mock.patch.object(
            JWTService, "decode_token", new=new_decode_token
        ):
            request = RequestTest()
            request.method = REQUESTS_WITH_AUTH[0]["method"]
            request.url.path = REQUESTS_WITH_AUTH[0]["path"]
            request.headers["authorization"] = "Bearer FALSE_AuthToken"
            middleware = AuthorizationMiddleware(app=ASGIApp, blacklisted_repo=BlacklistedTokenRepository(engine))
            response = await middleware.dispatch_func(
                request=request, call_next=new_call_next
            )
            response_content = json.loads(response.body.decode("utf-8"))
            assert response_content == "Incorrect Authorization Token"
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


    async def test_token_with_incorrect_signature(self, engine: AsyncEngine) -> None:
        request = RequestTest()
        request.method = REQUESTS_WITH_AUTH[0]["method"]
        request.url.path = REQUESTS_WITH_AUTH[0]["path"]
        request.headers["authorization"] = "incorrect-token"
        middleware = AuthorizationMiddleware(app=ASGIApp, blacklisted_repo=BlacklistedTokenRepository(engine))
        response = await middleware.dispatch_func(
            request=request, call_next=new_call_next
        )
        response_content = json.loads(response.body.decode("utf-8"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_content == "Incorrect Authorization Token"