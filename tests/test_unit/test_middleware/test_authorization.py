import pytest
import mock
from src.business_logic.services.jwt_token import JWTService
from src.presentation.api.middleware.authorization_validation import AuthorizationMiddleware, REQUESTS_WITH_AUTH
from starlette.types import ASGIApp
from fastapi import status
from src.presentation.api import router

async def new_decode_token(*args, **kwargs):
    if "Bearer AuthToken" in args or "Bearer AuthToken" in kwargs.values():
        return True
    else:
        return False

async def new_call_next(*args, **kwargs):
    return "Successful"

class NewUrl():
    def __init__(self) -> None:
        self.path = "" 

class NewRequest():    
    def __init__(self) -> None:
        self.url = NewUrl()
        self.method = ""
        self.headers = {
            "authorization" : None, 
            'auth-swagger' : None
        }


@pytest.mark.asyncio
class TestAuthorizationMiddleware:
    async def test_successful_auth(self):

        test_token = "Bearer AuthToken"
        request = NewRequest()

        with mock.patch.object(
            JWTService, "decode_token", new= new_decode_token
        ):
            for request_with_auth in REQUESTS_WITH_AUTH:
                request = NewRequest()
                request.method = request_with_auth["method"]
                request.url.path = request_with_auth["path"]
                request.headers["authorization"] = test_token

                middleware = AuthorizationMiddleware(app = ASGIApp)
                assert await middleware.dispatch_func(request=request, call_next=new_call_next) == 'Successful'
    
    async def test_successful_auth_with_swagger(self):

        test_token = "Bearer AuthToken"
        request = NewRequest()

        with mock.patch.object(
            JWTService, "decode_token", new= new_decode_token
        ):
            for request_with_auth in REQUESTS_WITH_AUTH:
                request = NewRequest()
                request.method = request_with_auth["method"]
                request.url.path = request_with_auth["path"]
                request.headers['auth-swagger'] = test_token

                middleware = AuthorizationMiddleware(app = ASGIApp)
                assert await middleware.dispatch_func(request=request, call_next=new_call_next) == 'Successful'

    async def test_without_token(self):
        request = NewRequest()
        request.method = REQUESTS_WITH_AUTH[0]["method"]
        request.url.path = REQUESTS_WITH_AUTH[0]["path"]
        middleware = AuthorizationMiddleware(app = ASGIApp)
        response = await middleware.dispatch_func(request=request, call_next=new_call_next) 
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_incorrect_token(self):
        with mock.patch.object(
            JWTService, "decode_token", new= new_decode_token
        ):
            request = NewRequest()
            request.method = REQUESTS_WITH_AUTH[0]["method"]
            request.url.path = REQUESTS_WITH_AUTH[0]["path"]
            request.headers["authorization"] = "Bearer FALSE_AuthToken"
            middleware = AuthorizationMiddleware(app = ASGIApp)
            response = await middleware.dispatch_func(request=request, call_next=new_call_next) 
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_all_REQUESTS_WITH_AUTH_possible(self):  
        
        correct_path_metod_dict = [{"path": api_route.path, "method": list(api_route.methods)[0] } for api_route in router.routes]
        
        for request_with_auth in REQUESTS_WITH_AUTH:
            assert request_with_auth in correct_path_metod_dict

    