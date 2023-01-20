from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from src.business_logic.services import TokenService, JWTService
from src.presentation.api.models.revoke import BodyRequestRevokeModel
from src.data_access.postgresql.errors import GrantNotFoundError
import logging
from typing import Union

logger = logging.getLogger('is_app')

revoke_router = APIRouter(
    prefix='/revoke',
)


@revoke_router.post('/', status_code= 200, tags=['Revoke'])
async def post_revoke_token(
    request: Request, 
    auth_swagger: Union[str, None] = Header(default=None, description="Authorization"),  #crutch for swagger
    request_body : BodyRequestRevokeModel= Depends(), 
    token_class: TokenService = Depends()
    ):

    try:
        token_class = token_class
        token_class.request = request
        
        token = request.headers.get('authorization')

        if token != None:
            token_class.authorization = token
        elif auth_swagger != None:
            token_class.authorization = auth_swagger
        else:
            raise PermissionError
        
        token_class.request_body= request_body

        logger.info(f'Revoking for token {request_body.token} started')
        return await token_class.revoke_token()

    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Token")  
    except GrantNotFoundError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Token")


@revoke_router.get('/test_token', status_code= 200, tags=['Revoke'])
async def get_test_token(
    request: Request
):
    return await JWTService().encode_jwt(payload={"sub": "1"})
