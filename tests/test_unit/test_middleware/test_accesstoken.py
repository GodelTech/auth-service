import pytest
import mock
from src.business_logic.services.jwt_token import JWTService
from src.presentation.api.middleware.access_token_validation import AccessTokenMiddleware
from starlette.types import ASGIApp
from fastapi import status
from src.presentation.api import router

async def new_decode_token(*args, **kwargs):
    if "Bearer AccessToken" in kwargs.values():
        return True
    else:
        return False

async def new_call_next(*args, **kwargs):
    return "Successful"

class NewUrl():
    def __init__(self) -> None:
        self.path = "/administration/" 

class NewRequest():    
    def __init__(self) -> None:
        self.url = NewUrl()
        self.method = ""
        self.headers = {
            "access-token" : None, 
        }
class NewJWTService:
    async def verify_token(self, *args, **kwargs):
        if "Bearer AccessToken" in kwargs.values() or "Bearer AccessToken" in args:
            return True
        else:
            return False

@pytest.mark.asyncio
class TestAccessTokenMiddleware:
    async def test_successful_auth(self):

        test_token = "Bearer AccessToken"
        request = NewRequest()


        request.headers["access-token"] = test_token

        middleware = AccessTokenMiddleware(app = ASGIApp, jwt_service=NewJWTService())
        assert await middleware.dispatch_func(request=request, call_next=new_call_next) == 'Successful'
    
    async def test_without_token(self):
        request = NewRequest()
        middleware = AccessTokenMiddleware(app = ASGIApp)
        response = await middleware.dispatch_func(request=request, call_next=new_call_next) 
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_incorrect_token(self):
        with mock.patch.object(
            JWTService, "verify_token", new= new_decode_token
        ):
            request = NewRequest()
            request.headers["authorization"] = "Bearer FALSE_accessToken"
            middleware = AccessTokenMiddleware(app = ASGIApp)
            response = await middleware.dispatch_func(request=request, call_next=new_call_next) 
            assert response.status_code == status.HTTP_403_FORBIDDEN


    