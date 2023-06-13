import pytest
import mock
from src.business_logic.services.jwt_token import JWTService
from src.presentation.middleware.access_token_validation import access_token_middleware
from starlette.types import ASGIApp
from fastapi import status
from src.presentation.api import router
from src.data_access.postgresql.repositories import BlacklistedTokenRepository
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from typing import Any

async def new_decode_token(*args: Any, **kwargs: Any) -> bool:
        return True
    
async def new_call_next(*args: Any, **kwargs: Any) -> str:
    return "Successful"

class NewUrl():
    def __init__(self) -> None:
        self.path = "/administration/" 

from sqlalchemy.ext.asyncio import AsyncSession

class NewRequest():    
    def __init__(self, session: AsyncSession, with_state:bool = True) -> None:
        self.url = NewUrl()
        self.method = ""
        self.headers: dict[str, Any] = {
            "access-token" : None, 
        }
        if with_state:
            self.state = NewRequest(session, with_state=False)
        self.session = session

# class NewJWTService(JWTService):
#     async def verify_token(self, *args: Any, **kwargs: Any) -> bool:
#         if "Bearer AccessToken" in kwargs.values() or "Bearer AccessToken" in args:
#             return True
#         else:
#             return False

@pytest.mark.asyncio
class TestAccessTokenMiddleware:
    async def test_successful_auth(self, connection: AsyncSession) -> None:
        test_token = "Bearer AccessToken"
        with mock.patch.object(
            JWTService, "decode_token", new=new_decode_token
        ):
            request = NewRequest(connection)

            request.headers["access-token"] = test_token

            middleware = await access_token_middleware(request=request, session=connection)
            assert middleware is None
    
    # async def test_without_token(self, connection: AsyncSession) -> None:
    #     request = NewRequest(connection)
    #     middleware = AccessTokenMiddleware(app = ASGIApp, jwt_service=NewJWTService())
    #     response = await middleware.dispatch_func(request=request, call_next=new_call_next) 
    #     assert response.status_code == status.HTTP_403_FORBIDDEN

    # async def test_incorrect_token(self,  connection: AsyncSession) -> None:
    #     with mock.patch.object(
    #         JWTService, "verify_token", new= new_decode_token
    #     ):
    #         request = NewRequest(connection)
    #         request.headers["authorization"] = "Bearer FALSE_accessToken"
    #         middleware = AccessTokenMiddleware(app = ASGIApp, jwt_service=NewJWTService())
    #         response = await middleware.dispatch_func(request=request, call_next=new_call_next) 
    #         assert response.status_code == status.HTTP_403_FORBIDDEN


    